import grpc

from app.core.grpc_clients import vectorizer_pb2_grpc, vectorizer_pb2


class VectorizerManager:
    def __init__(self, server_address: str | None = None):
        self.server_address = server_address
        self._channel = None
        self._stub = None

    async def __aenter__(self):
        if not self.server_address:
            return

        # создание асинхронного gRPC-канала
        self._channel = grpc.aio.insecure_channel(self.server_address)
        self._stub = vectorizer_pb2_grpc.VectorizerServiceStub(self._channel)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._channel:
            await self._channel.close()

    async def embed_text(self, text: str) -> list[float]:
        """
        Векторизация текста
        """

        if not self.server_address:
            return []

        if not self._stub:
            raise RuntimeError("Клиент не инициализирован")

        request = vectorizer_pb2.EmbedTextRequest(text=text)  # noqa

        try:
            response = await self._stub.EmbedText(request)
            return list(response.embedding)

        except grpc.aio.AioRpcError as ex:
            raise RuntimeError(f"Ошибка gRPC: {ex.code()}, {ex.details()}")

        except Exception as ex:
            raise RuntimeError(f"Произошла ошибка: {ex}")
