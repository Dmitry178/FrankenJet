import math

from fastembed import TextEmbedding
from typing import List

from app.config import app_settings
from app.logs import app_logger


class EmbeddingModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        app_logger.info(f"Initializing embedding model: {self.model_name}")
        self.model = TextEmbedding(
            model_name=model_name,
            cache_dir=app_settings.FASTEMBED_CACHE_DIR
        )
        app_logger.info("Embedding model loaded successfully")

    def embed(self, text: str) -> List[float]:
        """
        Векторизация текста
        """

        # embeddings_generator = self.model.embed([text])
        # embedding_vector = next(embeddings_generator)
        # return embedding_vector.tolist()

        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Пакетная векторизация текста
        """

        embeddings_generator = self.model.embed(texts)
        return [embedding.tolist() for embedding in embeddings_generator]

    @staticmethod
    def cosine_similarity(vector1: List[float], vector2: List[float]) -> float:
        """
        Вычисление косинусного сходства между двумя векторами
        """

        if len(vector1) != len(vector2):
            raise ValueError("Векторы должны быть одинаковой длины")

        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def cosine_similarity_texts(self, text1: str, text2: str) -> float:
        """
        Вычисление косинусного сходства между двумя текстами
        """

        embedding1 = self.embed(text1)
        embedding2 = self.embed(text2)

        return self.cosine_similarity(embedding1, embedding2)

    @staticmethod
    def euclidean_distance(vector1: List[float], vector2: List[float]) -> float:
        """
        Вычисление евклидова расстояния между двумя векторами
        """

        if len(vector1) != len(vector2):
            raise ValueError("Векторы должны быть одинаковой длины")

        squared_diffs = [(a - b) ** 2 for a, b in zip(vector1, vector2)]
        
        return math.sqrt(sum(squared_diffs))

    def euclidean_distance_texts(self, text1: str, text2: str) -> float:
        """
        Вычисление евклидова расстояния между двумя текстами
        """

        embedding1 = self.embed(text1)
        embedding2 = self.embed(text2)

        return self.euclidean_distance(embedding1, embedding2)

    def find_most_similar_by_vector(
            self,
            query_vector: List[float],
            candidates: List[List[float]],
            top_k: int = 5,
            similarity_func: str = "cosine"
    ) -> List[tuple]:
        """
        Поиск наиболее похожих векторов из списка кандидатов к заданному вектору запроса

        :param query_vector: Вектор запроса.
        :param candidates: Список векторов-кандидатов.
        :param top_k: Количество наиболее похожих результатов для возврата.
        :param similarity_func: Функция сходства ("cosine" или "euclidean").
        :return: Список кортежей (индекс_кандидата, значение_сходства), отсортированный по убыванию сходства.
        """

        similarities = []

        for i, candidate_vector in enumerate(candidates):
            if similarity_func == "cosine":
                score = self.cosine_similarity(query_vector, candidate_vector)
            elif similarity_func == "euclidean":
                # возврат отрицательного евклидово расстояния,
                # чтобы сортировка по убыванию работала как "наиболее близкие"
                score = -self.euclidean_distance(query_vector, candidate_vector)
            else:
                raise ValueError(f"Неизвестная функция сходства: {similarity_func}")

            similarities.append((i, score))

        # сортировка по значению сходства в порядке убывания
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def find_most_similar_by_text(
            self,
            query_text: str,
            candidate_texts: List[str],
            top_k: int = 5,
            similarity_func: str = "cosine"
    ) -> List[tuple]:
        """
        Поиск наиболее похожих текстов из списка кандидатов к заданному тексту запроса

        :param query_text: Текст запроса.
        :param candidate_texts: Список текстов-кандидатов.
        :param top_k: Количество наиболее похожих результатов для возврата.
        :param similarity_func: Функция сходства ("cosine" или "euclidean").

        :returns: Список кортежей (индекс_кандидата, значение_сходства, текст_кандидата),
            отсортированный по убыванию сходства.
        """

        query_vector = self.embed(query_text)
        candidate_vectors = self.embed_batch(candidate_texts)

        similarities_with_indices = self.find_most_similar_by_vector(
            query_vector, candidate_vectors, top_k, similarity_func
        )

        # добавляем сам текст кандидата в результат
        result = [
            (idx, score, candidate_texts[idx])
            for idx, score in similarities_with_indices
        ]

        return result
