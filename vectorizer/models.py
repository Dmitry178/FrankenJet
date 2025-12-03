"""
Вывод списка моделей, поддерживаемых FastEmbed
"""

from fastembed import TextEmbedding

# из подходящих для данного проекта:
# модель: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, размерность: 384
# модель: sentence-transformers/paraphrase-multilingual-mpnet-base-v2, размерность: 768

supported_models = TextEmbedding.list_supported_models()
for model in supported_models:
    print(model)
