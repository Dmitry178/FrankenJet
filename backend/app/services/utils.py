from sqlalchemy.dialects import postgresql


def get_raw_sql(query):
    compiled_query = query.compile(
        dialect=postgresql.dialect(),
        compile_kwargs={"literal_binds": True}
    )
    print(compiled_query)
