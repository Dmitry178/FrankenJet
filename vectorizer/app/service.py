import grpc

from concurrent import futures

from proto import vectorizer_pb2_grpc, vectorizer_pb2
from app.config import app_settings
from app.logs import app_logger
from app.models import EmbeddingModel


class VectorizerService(vectorizer_pb2_grpc.VectorizerServiceServicer):
    def __init__(self):
        # инициализация модели векторизации
        self.embedding_model = EmbeddingModel(model_name=app_settings.MODEL_NAME)

    def EmbedText(self, request: vectorizer_pb2.EmbedTextRequest, context) -> vectorizer_pb2.EmbedTextResponse:  # noqa
        """
        Реализация RPC метода EmbedText (векторизация текста)
        """

        try:
            # преобразование текста в вектор
            embedding = self.embedding_model.embed(request.text)

            # создание объекта ответа клиенту
            response = vectorizer_pb2.EmbedTextResponse(embedding=embedding)  # noqa

            return response

        except Exception as ex:
            app_logger.error(f"Ошибка генерации вектора: {ex}")
            context.set_code(grpc.StatusCode.INTERNAL)  # установка кода ошибки gRPC на INTERNAL
            context.set_details(str(ex))
            return vectorizer_pb2.EmbedTextResponse(embedding=[])  # noqa

    def EmbedTextBatch(
            self,
            request: vectorizer_pb2.EmbedTextBatchRequest,  # noqa
            context
    ) -> vectorizer_pb2.EmbedTextBatchResponse:  # noqa
        """
        Реализация RPC метода EmbedTextBatch (пакетная векторизация текста)
        """

        try:
            # преобразование массива текстов в массив векторов
            embeddings = self.embedding_model.embed_batch(request.text)

            # создание объектов EmbeddingResult для каждого эмбеддинга
            embedding_results = []
            for embedding_vector in embeddings:
                embedding_result = vectorizer_pb2.EmbeddingResult(embedding=embedding_vector)  # noqa
                embedding_results.append(embedding_result)

            # создание объекта ответа клиенту
            response = vectorizer_pb2.EmbedTextBatchResponse(embeddings=embedding_results)  # noqa

            return response

        except Exception as ex:
            app_logger.error(f"Ошибка генерации векторов: {ex}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(ex))
            return vectorizer_pb2.EmbedTextBatchResponse(embedding=[])  # noqa


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vectorizer_pb2_grpc.add_VectorizerServiceServicer_to_server(VectorizerService(), server)

    listen_addr = f"{app_settings.GRPC_HOST}:{app_settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    app_logger.info(f"Starting gRPC service on {listen_addr}")
    server.start()
    server.wait_for_termination()


service_instance = VectorizerService()
