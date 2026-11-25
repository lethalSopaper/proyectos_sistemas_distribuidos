FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ ./proto/
COPY src/ ./src/

RUN python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/cluster.proto

ENV PYTHONPATH=/app/src
CMD ["python", "src/server.py"]