# Noupe-local/app/providers/noupe_provider.py

import httpx
import json
import uuid
import time
import traceback
import asyncio
from typing import Dict, Any, AsyncGenerator, Union, List

from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

from app.providers.base_provider import BaseProvider
from app.core.config import settings

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NoupeProvider(BaseProvider):
    """
    Noupe/Jotform 聊天机器人提供商 (v1.3 最终揭秘版)
    - 【最终修正】揭示并处理了 Noupe API“伪流式”的真相，从正确的事件中提取一次性返回的完整答案。
    - 【优化】将一次性获取的答案模拟成流式返回，或在非流式模式下直接返回，确保客户端总能收到数据。
    - 实现了对话历史（上下文）传递的尝试。
    - 遵循 lzA6 的黄金标准架构。
    """

    async def chat_completion(self, request_data: Dict[str, Any], original_request: Request) -> Union[StreamingResponse, JSONResponse]:
        """
        处理聊天请求的核心入口。
        """
        try:
            headers = self._prepare_headers()
            payload = self._prepare_payload(request_data)
            model_name = request_data.get("model", "noupe-chat-model")
            url = f"https://www.noupe.com/API/ai-agent/{settings.AGENT_ID}/chats/{settings.CHAT_ID}"
            params = {
                "allowMultipleActions": "1",
                "masterPrompt": "1",
                "noBuffering": "1"
            }

            is_stream = request_data.get("stream", False)

            # Noupe API 的行为是“伪流式”，我们总是先获取完整内容
            logger.info(f"正在向 Noupe API 发送请求，准备捕获一次性返回的完整答案...")
            full_content = await self._get_full_response_from_stream(url, headers, params, payload)

            if not full_content:
                logger.error("未能从 Noupe API 的任何事件中提取到有效回复内容。")
                raise HTTPException(status_code=500, detail="未能从上游服务获取有效回复。")

            if is_stream:
                logger.info(f"已获取完整内容，现在开始模拟流式响应...")
                return StreamingResponse(
                    self._simulate_stream_from_full_content(full_content, model_name),
                    media_type="text/event-stream"
                )
            else:
                logger.info(f"已获取完整内容，正在返回非流式 JSON 响应...")
                return JSONResponse({
                    "id": f"chatcmpl-{uuid.uuid4().hex}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model_name,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": full_content
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                })

        except Exception as e:
            logger.error(f"处理 Noupe 请求时出错: {type(e).__name__}: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"处理 Noupe 请求时发生内部错误: {e}")

    async def _get_full_response_from_stream(self, url: str, headers: Dict, params: Dict, payload: Dict) -> str:
        """
        从 Noupe 的“伪流式”响应中捕获并返回第一个找到的完整答案。
        """
        full_content = ""
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                async with client.stream("POST", url, headers=headers, params=params, json=payload) as response:
                    logger.info(f"HTTP Request: {response.request.method} {response.request.url} \"HTTP/{response.http_version} {response.status_code} {response.reason_phrase}\"")
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        
                        try:
                            noupe_data = json.loads(line)
                            
                            if not isinstance(noupe_data, dict):
                                continue

                            # --- 终极核心修正：广撒网，从两个可能的路径捕获答案 ---
                            # 路径 1: 从 'chatbot_openai_request' 的 'end' 事件中提取
                            content_path1 = noupe_data.get("parameters", {}).get("chatResponse", {}).get("content")
                            if isinstance(content_path1, str) and content_path1:
                                logger.info(f"   [Capture Path 1] 成功从 'chatResponse.content' 捕获到完整答案。")
                                full_content = content_path1
                                break # 见好就收，立即跳出循环

                            # 路径 2: 从 'responseCode: 200' 的最终消息中提取
                            content_path2 = noupe_data.get("content", {}).get("message")
                            if isinstance(content_path2, str) and content_path2:
                                logger.info(f"   [Capture Path 2] 成功从 'content.message' 捕获到完整答案。")
                                full_content = content_path2
                                break # 见好就收，立即跳出循环
                            
                            logger.info(f"   [Stream Skip] 跳过不含目标答案的数据块: {noupe_data}")
                                
                        except json.JSONDecodeError:
                            logger.warning(f"   [Warning] JSON 解析失败，跳过此行: {line}")
                            continue
        
        except Exception as e:
            logger.error(f"   [Error] 在从流中获取完整响应时发生错误: {e}")
            traceback.print_exc()
        
        logger.info(f"从流中提取内容结束，最终内容长度: {len(full_content)}")
        return full_content

    async def _simulate_stream_from_full_content(self, full_content: str, model_name: str) -> AsyncGenerator[str, None]:
        """
        将一个完整的字符串模拟成 OpenAI 的流式响应。
        """
        chat_id = f"chatcmpl-{uuid.uuid4().hex}"
        
        # 1. 发送角色信息块
        role_chunk = {
            "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]
        }
        yield f"data: {json.dumps(role_chunk, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.01) # 短暂延迟，模拟网络传输

        # 2. 逐字发送内容块
        for char in full_content:
            delta_chunk = {
                "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
                "choices": [{"index": 0, "delta": {"content": char}, "finish_reason": None}]
            }
            yield f"data: {json.dumps(delta_chunk, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01) # 模拟打字效果

        # 3. 发送终止块
        final_chunk = {
            "id": chat_id, "object": "chat.completion.chunk", "created": int(time.time()), "model": model_name,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
        }
        yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
        
        # 4. 发送 [DONE] 信号
        yield "data: [DONE]\n\n"
        logger.info("   [Simulated Stream] 模拟流式传输结束。")


    def _prepare_headers(self) -> Dict[str, str]:
        if not settings.NOUPE_COOKIE:
            raise ValueError("NOUPE_COOKIE 未在 .env 文件中配置。")
        return {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Cookie": settings.NOUPE_COOKIE,
            "Origin": "https://www.noupe.com",
            "Referer": f"https://www.noupe.com/agent/{settings.AGENT_ID}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

    def _prepare_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = request_data.get("messages", [])
        
        last_user_message = next((msg["content"] for msg in reversed(messages) if msg["role"] == "user"), "")
        if not last_user_message:
            raise ValueError("请求中未找到用户消息。")
        
        return {
            "chatID": settings.CHAT_ID,
            "answer": last_user_message,
            "answerType": None,
            "isFirstQuestion": len(messages) <= 1,
            "isPastQuestion": len(messages) > 1,
            "conversationFeedback": False,
            "messageHistory": [],
            "platform": "embed",
            "messageType": "USER",
            "embedMode": "popover",
            "chatProps": {
                "isOneOne": False,
                "isMasterPrompt": True,
                "isFormCopilot": False,
                "isFormBuilderCopilot": False,
                "embedModeVariant": "noupeAgent"
            },
            "messageProps": {"isVoice": False},
            "screenShareActive": False
        }
