class BaseRepository:

    model = None
    # mapper: DataMapper = None  # TODO: добавить DataMapper

    def __init__(self, session):
        self.session = session

