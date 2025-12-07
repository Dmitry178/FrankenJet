from app.config.app import RAGBOT_INDEX_NAME
from app.core import ESManager, VectorizerManager


class RagBotService:

    es: ESManager | None
    vect: VectorizerManager | None

    def __init__(self, es: ESManager | None = None, vectorizer: VectorizerManager | None = None) -> None:
        self.es = es
        self.vectorizer = vectorizer
        self.index = [RAGBOT_INDEX_NAME]

    async def get_top_chunks(self, query_text: str, top_k: int = 3) -> list[dict]:
        """
        Поиск наиболее подходящих чанков в Elasticsearch (с оценкой релевантности)
        """

        # векторизация текста запроса
        embedding = (await self.vectorizer.embed_text_batch([query_text]))[0]

        # поиск в Elasticsearch
        knn_query = {
            "field": "vector",
            "query_vector": embedding,
            "k": top_k,
            "num_candidates": top_k * 2
        }

        search_body = {
            "knn": knn_query,
            "_source": ["text", "metadata"]
        }

        response = await self.es.search(query=search_body, index=RAGBOT_INDEX_NAME)
        hits = response["hits"]["hits"]

        # извлечение текста и метаданных из результата
        top_chunks = [
            {
                "text": hit["_source"]["text"],
                "score": hit["_score"]  # оценка релевантности
            }
            for hit in hits
        ]

        return top_chunks

    async def get_top_chunks_list(self, query_text: str, top_k: int = 3) -> list[str]:
        """
        Поиск наиболее подходящих чанков в Elasticsearch (список)
        """

        chunks = await self.get_top_chunks(query_text, top_k)
        return [chunk["text"] for chunk in chunks]
