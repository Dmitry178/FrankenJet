""" Вывод списка моделей, поддерживаемых FastEmbed """

from fastembed import TextEmbedding

# из подходящих для данного проекта:
# модель: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2, размерность: 384
# модель: sentence-transformers/paraphrase-multilingual-mpnet-base-v2, размерность: 768

supported_models = TextEmbedding.list_supported_models()
for model in supported_models:
    print(model)


""" Вывод списка моделей, поддерживаемых Sentence Transformers """

from huggingface_hub import list_models

# поиск моделей, связанных с sentence-transformers
models = list_models(filter="sentence-transformers", sort="downloads", direction=-1)

print("Модели, помеченные как 'sentence-transformers':")
for model in models:
    print(f"- {model.id}")
