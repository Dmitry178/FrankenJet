from fastapi.params import Example

login_example = {
    "example": Example(
        summary="Default login",
        value={
            "email": "user@example.com",
            "password": "password",
        }
    )
}
