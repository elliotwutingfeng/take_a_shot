FROM ghcr.io/astral-sh/uv:python3.13-alpine
LABEL maintainer=wutingfeng@outlook.com

ENV PYTHONUNBUFFERED=True

RUN apk add --no-cache \
    chromium-chromedriver \
    font-noto \
    freetype \
    ttf-freefont \
    && rm -rf /var/cache/apk/*

ENV CHROME_BIN=/usr/bin/chromium-browser

RUN addgroup -S unprivilegeduser && adduser -S unprivilegeduser -G unprivilegeduser
USER unprivilegeduser
WORKDIR /home/unprivilegeduser

COPY --chown=unprivilegeduser:unprivilegeduser pyproject.toml uv.lock takeashot.py ./
RUN uv lock && uv sync --locked --all-groups

ENTRYPOINT ["uv", "run", "takeashot.py"]
CMD ["--help"]
