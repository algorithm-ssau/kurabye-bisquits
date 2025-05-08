class ProductNotFoundException(Exception):
    def __init__(self, message: str = "Product is't found"):
        super().__init__(message)
