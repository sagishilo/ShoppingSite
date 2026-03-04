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

    def item_not_found_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The item was not found"
        )

    def item_not_fav_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The item is not a favorite"
        )

    def item_fav_already_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The item is already a favorite"
        )
    def itemname_taken_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided item already exist"
        )

    def order_not_found_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided order was not found"
        )

    def invalid_order_status_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided order status not valid"
        )


    def item_in_order_not_found_exception(self):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided item was not found in the order"
        )

    def temp_order_exist(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user has an open order already"
        )

    def closed_order(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to add items to a closed order"
        )
    def not_in_stock(self, in_stock):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unable to add this amount - {in_stock} left in stock"
        )
    def token_exception(self):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token provided is invalid"
        )
