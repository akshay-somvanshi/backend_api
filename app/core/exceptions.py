class DatabaseError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error

class StorageError(Exception):
    def __init__(self, message, error):
        super().__init__(message)
        self.error = error 