from enum import Enum


class RequestTypeEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ProtocolTypeEnum(str, Enum):
    HTTP = "HTTP"
