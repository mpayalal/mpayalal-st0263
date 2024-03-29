from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Request(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: bytes
    def __init__(self, resource: _Optional[bytes] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: str
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[str] = ...) -> None: ...

class RequestSimple(_message.Message):
    __slots__ = ("resource",)
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    resource: bytes
    def __init__(self, resource: _Optional[bytes] = ...) -> None: ...

class ResponseSimple(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: str
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[str] = ...) -> None: ...

class openRequest(_message.Message):
    __slots__ = ("fileName", "mode")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    mode: str
    def __init__(self, fileName: _Optional[str] = ..., mode: _Optional[str] = ...) -> None: ...

class openResponse(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: str
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[str] = ...) -> None: ...

class readRequest(_message.Message):
    __slots__ = ("fileName", "chunkUrl")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHUNKURL_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    chunkUrl: str
    def __init__(self, fileName: _Optional[str] = ..., chunkUrl: _Optional[str] = ...) -> None: ...

class readResponse(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: bytes
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[bytes] = ...) -> None: ...

class writeRequest(_message.Message):
    __slots__ = ("fileName", "chunkUrl", "data")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    CHUNKURL_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    chunkUrl: str
    data: bytes
    def __init__(self, fileName: _Optional[str] = ..., chunkUrl: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class writeResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...
