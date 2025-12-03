from fastembed import TextEmbedding
from typing import List

from app.logs import app_logger


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        app_logger.info(f"Initializing embedding model: {self.model_name}")
        # fastembed кэширует модель в ~/.cache/fastembed
        self.model = TextEmbedding(model_name=model_name)
        app_logger.info("Embedding model loaded successfully")

    def embed(self, text: str) -> List[float]:
        """
        Векторизация текста
        """

        embeddings_generator = self.model.embed([text])
        embedding_vector = next(embeddings_generator)
        return embedding_vector.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Пакетная векторизация текста
        """

        embeddings_generator = self.model.embed(texts)
        return [embedding.tolist() for embedding in embeddings_generator]
