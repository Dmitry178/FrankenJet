FROM python:3.12.12-slim-bookworm

ENV TZ="Europe/Moscow"

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./pyproject.toml ./uv.lock* /code/
RUN pip install uv
RUN uv pip compile pyproject.toml --output-file requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src
COPY ./proto /code/proto
COPY ./server.py /code/server.py

CMD ["python", "server.py"]
