# The machine each bench run works in: a normal dev box Claude can use freely,
# with a browser it can drive, but nothing of yours on it. Both arms use it.
FROM mcr.microsoft.com/playwright:v1.52.0-noble
ARG CLAUDE_VERSION=2.1.322
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip python3-venv git ripgrep \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g @anthropic-ai/claude-code@${CLAUDE_VERSION} \
 && mkdir -p /work /cfg /plugin && chown pwuser /work /cfg \
 && chrome=$(ls -d /ms-playwright/chromium-*/chrome-linux/chrome | head -1) \
 && printf '#!/bin/sh\nexec %s --no-sandbox "$@"\n' "$chrome" > /usr/local/bin/chromium && chmod +x /usr/local/bin/chromium \
 && for n in chromium-browser google-chrome chrome; do ln -s /usr/local/bin/chromium /usr/local/bin/$n; done
# The browser on the PATH under its usual names, as on a dev machine, so a run finds it without hunting.
# --no-sandbox because the container is the sandbox (Playwright passes the same flag itself).
ENV CHROME_PATH=/usr/local/bin/chromium PUPPETEER_EXECUTABLE_PATH=/usr/local/bin/chromium PUPPETEER_SKIP_DOWNLOAD=1
USER pwuser
ENV HOME=/home/pwuser CLAUDE_CONFIG_DIR=/cfg
WORKDIR /work
