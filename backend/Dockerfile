FROM python:3.11.11-slim-bookworm

ENV TZ="Europe/Moscow"

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./pyproject.toml ./uv.lock* /code/
RUN pip install uv
RUN uv exoprt > requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8111", "--forwarded-allow-ips=*", "--proxy-headers", "--no-server-header"]
