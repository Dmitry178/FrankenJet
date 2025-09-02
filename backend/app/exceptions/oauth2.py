from starlette import status


class BaseOAuth2Exception(Exception):
    detail = "Error"
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(self.detail, *args)


class OAuth2ErrorEx(BaseOAuth2Exception):
    detail = "OAuth2 error"
