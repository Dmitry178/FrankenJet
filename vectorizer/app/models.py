import math

from fastembed import TextEmbedding
from sentence_transformers import SentenceTransformer

from typing import List

from app.config import app_settings, ModelLib
from app.logs import app_logger


class EmbeddingModel:
    def __init__(self, model_name: str, model_lib: str):

        self.model = None
        self.model_lib = None
        self.model_name = None

        app_logger.info(f"Initializing embedding model: {model_name}")

        if model_lib == ModelLib.fastembed.name:
            self.model = TextEmbedding(
                model_name=model_name,
                cache_dir=app_settings.MODEL_CACHE_DIR,
            )

        elif model_lib == ModelLib.sentence_transformers.name:
            self.model = SentenceTransformer(
                model_name_or_path=model_name,
                # cache_folder=app_settings.MODEL_CACHE_DIR,
            )

        else:
            app_logger.error("Embedding model not loaded")
            return

        self.model_lib = model_lib
        self.model_name = model_name

        app_logger.info("Embedding model loaded successfully")

    def embed(self, text: str) -> List[float]:
        """
        Векторизация текста
        """

        if self.model_lib == ModelLib.fastembed:
            embeddings = list(self.model.embed([text]))
            return embeddings[0].tolist()

        elif self.model_lib == ModelLib.sentence_transformers:
            embedding = self.model.encode([text], convert_to_numpy=True)[0]
            return embedding.tolist()

        else:
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Пакетная векторизация текста
        """

        if self.model_lib == ModelLib.fastembed:
            embeddings_generator = self.model.embed(texts)
            return [embedding.tolist() for embedding in embeddings_generator]

        elif self.model_lib == ModelLib.sentence_transformers:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [embedding.tolist() for embedding in embeddings]

        else:
            return []

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

    def cosine_similarity_texts(self, text1: str, text2: str) -> float | None:
        """
        Вычисление косинусного сходства между двумя текстами
        """

        if not self.model:
            return None

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

    def euclidean_distance_texts(self, text1: str, text2: str) -> float | None:
        """
        Вычисление евклидова расстояния между двумя текстами
        """

        if not self.model:
            return None

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

        if not self.model:
            return []

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

        if not self.model:
            return []

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
