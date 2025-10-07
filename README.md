# Noupe-2api 🚀 - 一份宣言，一份蓝图，一份邀请

<div align="center">
  <img src="https://user-images.githubusercontent.com/10214336/230679957-9db19942-571a-4364-b15e-e0ec6a91753c.png" alt="Project Banner" width="600"/>
</div>

<p align="center">
  <strong>将任何 Noupe/Jotform 聊天机器人，转化为一个符合 OpenAI 标准的高性能、流式 API 接口。</strong>
  <br/>
  <em>这不仅仅是一个工具，这是我们对“万物皆可 API”信念的一次极致实践。</em>
</p>

<p align="center">
  <a href="https://github.com/lzA6/Noupe-2api/blob/main/LICENSE"><img src="https://img.shields.io/github/license/lzA6/Noupe-2api?style=for-the-badge&color=blue" alt="License"></a>
  <a href="https://hub.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker" alt="Docker Ready"></a>
  <a href="https://github.com/lzA6/Noupe-2api"><img src="https://img.shields.io/github/stars/lzA6/Noupe-2api?style=for-the-badge&logo=github" alt="GitHub Stars"></a>
</p>

---

## 📜 一份宣言：我们为何而战？

在一个被封闭花园和专有接口所定义的世界里，我们选择成为“破壁者”。我们坚信，每一个强大的 AI 服务，无论其前端多么华丽，其核心都应该能被解放、被连接、被重塑。`Noupe-2api` 就是这一信念的产物。

它源于一个简单而深刻的哲学：**“如果它能对话，它就能被 API 化。”**

我们拒绝满足于仅仅“使用”一个产品。我们渴望“驾驭”它。`Noupe-2api` 将 Noupe 聊天机器人从一个嵌入式的前端组件，升华为一个开发者可以随心所欲调用的、强大的、可编程的后端服务。这不仅是技术的转换，更是思想的解放。我们赋予了开发者用代码与 AI 对话的权力，将原本封闭的交互，变成了无限创意的源泉。

这，就是我们的战斗。这，就是 `Noupe-2api` 的灵魂。

## 🗺️ 一份蓝图：洞悉项目的宏伟架构

为了让你能像“上帝”一样俯瞰整个项目，我们为你绘制了这份架构蓝图。

### 🏛️ 项目文件结构

```
Noupe-local/
├── app/
│   ├── core/
│   │   └── config.py         # 🏛️ 中央大脑：定义所有环境变量和配置
│   └── providers/
│       ├── base_provider.py  # 📜 契约：所有 Provider 的抽象基类
│       └── noupe_provider.py # ❤️ 心脏：实现与 Noupe API 通信的核心逻辑
├── .env                      # 🔑 你的钥匙串：存放你的专属密钥和 ID
├── .env.example              # 🗺️ 地图：告诉你 .env 文件该如何填写
├── docker-compose.yml        # 🏗️ 总工程师：编排和启动所有服务
├── Dockerfile                # 🏭 工厂：构建后端 FastAPI 应用的镜像
├── main.py                   # 🚦 交通枢纽：FastAPI 应用的入口
├── nginx.conf                # 🚪 大门管家：Nginx 配置文件，负责反向代理和粘性会话
└── requirements.txt          # 📜 购物清单：项目所需的所有 Python 依赖
```

### 🌊 数据流转图

```mermaid
graph TD
    subgraph 用户侧
        A[你的应用 / 客户端]
    end

    subgraph Noupe-2api 服务 (运行于 Docker)
        B(Nginx:8080)
        C{Upstream: noupe_backend}
        D[FastAPI Worker 1]
        E[FastAPI Worker 2]
    end

    subgraph 外部服务
        F[Noupe/Jotform API]
    end

    A -- "POST /v1/chat/completions\n(携带 API_MASTER_KEY)" --> B
    B -- "粘性会话\n(基于 Cookie 哈希)" --> C
    C --> D
    D -- "携带你的 Cookie\n发送 POST 请求" --> F
    F -- "返回伪流式响应" --> D
    D -- "处理并模拟成真流式" --> B
    B -- "SSE 流式响应" --> A
```

## 🔬 一份深度报告：解构核心技术

### 🤖 技术原理剖析

#### 1. “伪流式”的真相与“模拟流式”的艺术 (⭐⭐⭐⭐⭐)

*   **技术术语 (The Jargon)**: `application/x-ndjson` (Newline Delimited JSON), 状态化解析器 (Stateful Parser), 异步生成器 (Async Generator)。
*   **大白话 (The Gist)**: 我们通过抓包发现，Noupe API 虽然声称自己是“流式”，但它并不像水龙头一样一个字一个字地流出数据。它更像一个急性子的厨师，在后厨做好了整盘菜（完整的回答），然后分两次，用两个不同的盘子（两个不同的 JSON 数据块），“Duang”一下全给你端上来了。
*   **我们的解决方案 (The Magic)**: `noupe_provider.py` 里的 `_get_full_response_from_stream` 函数就是我们的“火眼金睛”。它不再傻傻地等水滴，而是时刻准备着，只要看到那两个装着整盘菜的“盘子”中的任何一个，就立刻把菜端走（提取完整答案），然后忽略掉所有其他无关的盘子（控制消息）。接着，`_simulate_stream_from_full_content` 函数扮演一个优雅的服务员，把这盘菜（完整答案）用小勺一点一点地（一个字一个字地）喂给客户端，完美模拟出“打字机”的流式效果。
*   **难度评级**: ★★★★★ (5/5) - 这是逆向工程的艺术，需要敏锐的洞察力和对 API 行为的精准预判。

#### 2. “终极粘性会话”的奥秘 (⭐⭐⭐⭐)

*   **技术术语 (The Jargon)**: Nginx `hash` 指令, `consistent` 参数, `$http_cookie` 变量。
*   **大白话 (The Gist)**: 想象一下，你去一个有多个窗口的银行办理业务，你希望每次都由同一个柜员为你服务，因为他记得你的所有情况。Nginx 就是这个银行的大堂经理。Noupe API 通过 `Cookie` (就像你的身份证) 来识别你。我们的 `nginx.conf` 文件告诉大堂经理：“嘿，看这位顾客的身份证 (`$http_cookie`)，算一个哈希值，根据这个值，永远把他分配到同一个窗口（后端 FastAPI 实例）！”
*   **为何终极 (Why it's Ultimate)**: 这种方法比根据 IP 地址分配要可靠得多。因为你的 IP 可能会变，但只要你不清空浏览器缓存，你的“身份证”(`Cookie`) 就不会变。这确保了你的对话上下文永远不会因为被分配到“不认识你”的柜员那里而丢失。
*   **难度评级**: ★★★★☆ (4/5) - 理解 Nginx 的负载均衡策略并选择最优解，是构建高性能服务的关键。

### ✅ 项目优劣势对比

| 特性 | 👍 优点 (Pros) | 👎 缺点 (Cons) |
| :--- | :--- | :--- |
| **通用性** | **极致灵活**：通过修改 `.env` 文件，可以接入**任何** Noupe 机器人，而非写死。 | 需要用户具备基本的抓包能力来获取凭证。 |
| **性能** | **高性能**：基于 FastAPI 和 Uvicorn，异步非阻塞，性能卓越。Nginx 提供了强大的负载均衡和粘性会话。 | 响应速度完全依赖于上游 Noupe API 的速度。 |
| **兼容性** | **无缝对接**：输出完全兼容 OpenAI API 格式，可直接接入任何支持 OpenAI 的客户端。 | 未实现 OpenAI 的所有参数（如 `temperature`），因为 Noupe API 本身不支持。 |
| **部署** | **一键启动**：基于 Docker 和 Docker Compose，实现了真正的一键部署，跨平台无差异。 | 首次构建 Docker 镜像可能需要一些时间。 |

## 🧑‍🏫 一份保姆级教程：从零到你的第一个 API 调用

### 1. 准备工作：创建你自己的 Noupe 机器人

> 💡 **哲学时刻**: 在我们开始“索取”之前，我们必须先“创造”。这是第一步，也是最重要的一步。

1.  访问 [<sup>1</sup>](https://www.noupe.com/)。
2.  注册并登录，然后创建一个新的 AI 代理 (Agent)。你可以训练它，给它喂养你自己的知识库。
3.  完成创建后，进入“**获取您的代码 (Get Your Code)**”页面。你会看到类似下面的嵌入代码。**暂时不要关闭这个页面！**

    <img src="https://i.imgur.com/your-agent-id-screenshot.png" alt="获取 Agent ID" width="700"/>
    *(示例图：你需要在这个页面找到你的 Agent ID)*

### 2. 核心步骤：获取你的机器人“三件套”

> 💡 **黑客精神**: 这是整个过程中最有趣的部分，像一个侦探一样，从网络流量中找到属于你的宝藏。

这是将你的专属机器人与 `Noupe-2api` 连接起来的**唯一**一步。

1.  **创建本地测试文件**:
    *   在你的电脑上创建一个名为 `test.html` 的文件。
    *   将你在上一步获取的 `<script>...</script>` 嵌入代码，完整地粘贴到这个 HTML 文件中。你的文件看起来应该像这样：
        ```html
        <!DOCTYPE html>
        <html>
        <head><title>My Noupe Test</title></head>
        <body>
            <h1>My Bot Test Page</h1>
            <!-- 把你的嵌入代码粘贴在这里 -->
            <script src='https://www.noupe.com/embed/你的AGENT_ID.js'></script>
        </body>
        </html>
        ```

2.  **开始“抓包”**:
    *   用 Chrome 或 Edge 浏览器打开你刚刚创建的 `test.html` 文件。
    *   按下 `F12` 键，打开“开发者工具”。
    *   切换到“**网络 (Network)**”标签页。
    *   在页面右下角出现的聊天框里，**随便发送一条消息**，比如“你好”。

3.  **定位并复制**:
    *   在“网络”标签的请求列表中，你会看到一个新的请求出现。它的名称通常以 `POST` 方法，并指向 `https://www.noupe.com/API/ai-agent/...`。
    *   **找到你的 `CHAT_ID`**: 在这个请求的 URL 中，仔细查找 `/chats/` 后面的那串字符，它就是你的 `CHAT_ID`！
    *   **复制 cURL**: 右键点击这个请求，选择 **复制 (Copy)** > **以 cURL (bash) 格式复制 (Copy as cURL (bash))**。

    <img src="https://i.imgur.com/your-curl-screenshot.png" alt="抓取 cURL" width="700"/>
    *(示例图：右键点击核心请求，复制 cURL)*

4.  **提取 `Cookie`**:
    *   将复制的 cURL 命令粘贴到任何文本编辑器（如记事本、VS Code）中。
    *   在其中找到 `-H 'cookie: ...'` 或 `--cookie '...'` 的部分。
    *   **完整地**复制引号内的所有内容。这就是你的 `NOUPE_COOKIE`。

### 3. 一键部署：让魔法发生

> 💡 **开源精神**: 我们提供工具，你只需点燃引擎。

#### 方案一：Docker 一键部署 (推荐)

1.  **克隆本项目**:
    ```bash
    git clone https://github.com/lzA6/Noupe-2api.git
    cd Noupe-2api
    ```
2.  **配置你的凭证**:
    *   复制 `.env.example` 文件为 `.env`。
    *   打开 `.env` 文件，将你刚刚获取的 `AGENT_ID`, `CHAT_ID`, 和 `NOUPE_COOKIE` 填入其中。
    *   （可选）设置一个你自己的 `API_MASTER_KEY` 和 `NGINX_PORT`。
3.  **启动！**:
    ```bash
    docker-compose up -d --build
    ```
    等待 Docker 完成构建和启动。现在，你的 API 已经在 `http://localhost:8080` (或你设置的端口) 上运行了！

#### 方案二：Hugging Face Spaces 一键部署 (懒人福音)

> 🌍 让世界成为你的服务器！

![Deploy to Hugging Face Spaces [<sup>2</sup>](https://hf.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg)](https://huggingface.co/new-repo?template=lzA6/Noupe-2api)

点击上面的按钮，Hugging Face 会自动为你克隆这个仓库。你只需要在 `Secrets` 中添加你的 `AGENT_ID`, `CHAT_ID`, 和 `NOUPE_COOKIE`，然后点击“部署”，一切就都搞定了！

### 4. 验证与使用：与你的 AI 对话

现在，你可以使用任何支持 OpenAI API 格式的客户端来与你的 `Noupe-2api` 对话了。

*   **API 地址**: `http://localhost:8080` (或你的服务器地址)
*   **API 密钥**: 你在 `.env` 中设置的 `API_MASTER_KEY`
*   **模型名称**: `noupe-chat-model`

这是一个使用 `curl` 的例子：

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer你的API_MASTER_KEY" \
  -d '{
    "model": "noupe-chat-model",
    "messages": [
      {"role": "user", "content": "西红柿炒鸡蛋怎么做？"}
    ],
    "stream": true
  }'
```

## 🔭 未来展望：我们共同的星辰大海

`Noupe-2api` 只是一个开始。它证明了一个强大的理念，但它的边界等待着被我们共同拓宽。

### 🚀 近期计划 (Short-term Goals)

*   **[待实现] 智能 `messageHistory`**: 当前 `messageHistory` 为空以确保稳定。未来的版本将尝试解析 Noupe 的历史格式，或构建一个本地缓存来实现更强大的多轮对话记忆。
*   **[待实现] 错误处理增强**: 更精细地解析上游 API 可能返回的错误信息，并以 OpenAI 兼容的格式返回给客户端。
*   **[待优化] 配置热重载**: 研究如何在不重启 Docker 容器的情况下，动态更新 `.env` 中的 `Cookie` 等配置。

###🌌 长期愿景 (Long-term Vision)

*   **“万物2api” 框架**: 将 `Noupe-2api` 的核心架构抽象成一个更通用的 `*-2api` 框架。未来，适配一个新的网站可能只需要编写一个几十行的 `Provider` 子类，真正实现“万物皆可 API”。
*   **可视化配置界面**: 创建一个简单的 Web UI，让非开发者用户也能通过点击和粘贴，轻松配置和部署自己的 `2api` 服务。
*   **社区驱动的 Provider 市场**: 建立一个社区，让开发者可以提交和分享他们为各种网站编写的 `Provider`，形成一个丰富的生态系统。

## 🤝 一份邀请函：成为“破壁者”的一员

> 💡 **我们的信条**: 开源的伟大，不在于代码的多少，而在于参与者的多少。

`Noupe-2api` 不属于我，它属于每一个信仰开放、热爱创造的你。我们邀请你，无论你是代码大神，还是刚刚入门的小白，都加入到这场激动人心的“破壁”之旅中来。

*   **发现一个 Bug？** 👉 提交一个 Issue [<sup>3</sup>](https://github.com/lzA6/Noupe-2api/issues)！
*   **有一个绝妙的点子？** 👉 开启一个 Discussion [<sup>4</sup>](https://github.com/lzA6/Noupe-2api/discussions)！
*   **修复了一个问题或实现了一个新功能？** 👉 提交一个 Pull Request [<sup>5</sup>](https://github.com/lzA6/Noupe-2api/pulls)！

**你的每一次贡献，无论大小，都在为这个更开放、更互联的世界添砖加瓦。**

---

## ⚖️ 一份协议书：自由的基石

本项目采用 **Apache License 2.0** 许可。

这意味着你可以自由地使用、修改、分发甚至商业化本项目的代码，只需遵守许可协议的条款。我们相信，真正的自由是激发创新的土壤。

---

**感谢你的阅读。现在，让我们一起，去创造，去连接，去改变世界。**
