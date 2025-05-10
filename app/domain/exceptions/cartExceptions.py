class CartInsertError(Exception):
    def __init__(self, message: str = "Cart or product is't exists"):
        super().__init__(message)


class CartDeleteError(Exception):
    def __init__(self, message: str = "Cart or product doesn't exists."):
        super().__init__(message)
