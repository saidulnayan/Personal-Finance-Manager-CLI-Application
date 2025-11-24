class FinanceError(Exception):
    pass

class ValidationError(FinanceError):
    pass

class NotFoundError(FinanceError):
    pass

class StorageError(FinanceError):
    pass
