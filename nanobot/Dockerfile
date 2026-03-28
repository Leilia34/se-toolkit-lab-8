ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

WORKDIR /app

# Ставим git и зависимости
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir nanobot-ai mcp

# Копируем и ставим webchat
COPY nanobot-websocket-channel/nanobot-channel-protocol /tmp/nanobot-channel-protocol
COPY nanobot-websocket-channel/nanobot-webchat /tmp/nanobot-webchat
RUN pip install --no-cache-dir /tmp/nanobot-channel-protocol /tmp/nanobot-webchat

# Копируем и ставим mcp_lms
COPY mcp/mcp_lms /app/mcp_lms
RUN pip install --no-cache-dir /app/mcp_lms

# Копируем и ставим mcp_observability
COPY mcp/mcp_observability /app/mcp_observability
RUN pip install --no-cache-dir /app/mcp_observability

# Копируем конфиг
COPY nanobot/config.json /app/config.json

ENV NANOBOT_LMS_BACKEND_URL=http://backend:8000
ENV NANOBOT_LMS_API_KEY=lms-api-key
ENV LLM_API_BASE_URL=http://qwen-code-api:8080/v1
ENV VICTORIALOGS_URL=http://victorialogs:9428
ENV VICTORIATRACES_URL=http://victoriatraces:10428

CMD ["nanobot", "gateway", "--config", "/app/config.json", "--workspace", "/app"]
