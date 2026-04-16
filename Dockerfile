FROM python:alpine

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

COPY pyproject.toml .
COPY uv.lock .
ENV UV_NO_DEV=1
RUN uv sync --locked

COPY lappupeli lappupeli
COPY docker-entrypoint.sh .
COPY schema.sql .
RUN chmod +x docker-entrypoint.sh


EXPOSE 8000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["uv", "run",  "gunicorn", "-b", "0.0.0.0:8000", "--chdir", "./lappupeli" ,"app:create_app()"]
