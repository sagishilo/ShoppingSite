from fastapi import HTTPException, status


class CustomExceptions:

    def token_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token provided is invalid"
        )

    def username_taken_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided username already taken"
        )

    def user_credentials_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    def user_not_found_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user was not found"
        )