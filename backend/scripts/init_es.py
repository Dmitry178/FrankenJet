"""
Индексирование статей в ElasticSearch
"""

index_settings = {
    "settings": {
        "analysis": {
            "filter": {
                "city_synonyms": {
                    "type": "synonym",
                    "synonyms": [
                        "санкт-петербург, петербург, питер, спб, с-пб, с-петербург, петроград, ленинград",
                        "москва, мос, мск"
                        "екатеринбург, екат, ебург, ёбург, екб, свердловск"
                    ]
                }
            },
            "analyzer": {
                "my_synonym_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "icu_normalizer",
                        "lowercase",
                        "city_synonyms",
                        "russian_morphology",
                        "english_morphology",
                        "snowball"
                    ]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "my_synonym_analyzer"},
            "content": {"type": "text", "analyzer": "my_synonym_analyzer"},
            "tags": {"type": "keyword"},
            "entities": {"type": "keyword"}
        }
    }
}
