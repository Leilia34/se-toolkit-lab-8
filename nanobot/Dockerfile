ARG REGISTRY_PREFIX_DOCKER_HUB=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir nanobot-ai mcp mcp-observability

# Копируем webchat из submodule и ставим
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol /tmp/nanobot-channel-protocol
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat /tmp/nanobot-webchat
RUN pip install --no-cache-dir /tmp/nanobot-channel-protocol /tmp/nanobot-webchat

# Копируем mcp_lms и ставим
COPY --from=workspace mcp /app/mcp
RUN pip install --no-cache-dir /app/mcp

# Копируем конфиг и entrypoint
COPY config.json /app/config.json
COPY entrypoint.py /app/entrypoint.py

ENV NANOBOT_LMS_BACKEND_URL=http://backend:8000
ENV NANOBOT_LMS_API_KEY=lms-api-key
ENV LLM_API_BASE_URL=http://qwen-code-api:8080/v1

CMD ["python", "/app/entrypoint.py"]
