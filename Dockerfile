FROM python:3.11.5-alpine

WORKDIR /app

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-root --only main

COPY lappupeli lappupeli
COPY docker-entrypoint.sh .
COPY schema.sql .
RUN chmod +x docker-entrypoint.sh


EXPOSE 8000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD ["poetry", "run",  "gunicorn", "-b", "0.0.0.0:8000", "--chdir", "./lappupeli" ,"app:create_app()"]
