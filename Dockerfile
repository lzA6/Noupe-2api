# Noupe-local/Dockerfile

# 使用官方的 Python 3.10 slim 版本作为基础环境
FROM python:3.10-slim

# 设置环境变量，防止 Python 写入 .pyc 文件并确保输出无缓冲
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 设置工作目录
WORKDIR /app

# 复制整个项目结构到容器中
COPY . /app

# 设置环境变量，告诉 Python 模块的搜索路径，这是解决模块导入问题的关键
ENV PYTHONPATH=/app

# 安装所有 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 容器启动时要执行的命令
# 端口号 8000 是容器内部端口，将由 Nginx 代理
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
