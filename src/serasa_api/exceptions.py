"""Module for custom exceptions at Serasa API."""

class SerasaAPIException(Exception):
    def __init__(self, message: str, payload: dict = {}):
        self.message = message
        self.payload = payload

    def __repr__(self):
        """__repr__."""
        template = "{class_name}: {message}"
        return template.format(
            class_name=self.__class__.__name__, message=self.message
        )

    def __str__(self):
        return self.__repr__()

    def to_dict(self):
        rv = {
            "payload": self.payload,
            "type": self.__class__.__name__,
            "message": self.message,
        }
        return rv


class SerasaAPIQueryErrorException(SerasaAPIException):
    pass


class SerasaAPIMalformedOutputException(SerasaAPIException):
    pass


class SerasaAPILoginErrorException(SerasaAPIException):
    pass
