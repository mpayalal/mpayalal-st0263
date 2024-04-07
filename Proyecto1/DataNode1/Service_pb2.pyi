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
    __slots__ = ("resource", "fileName")
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    resource: str
    fileName: str
    def __init__(self, resource: _Optional[str] = ..., fileName: _Optional[str] = ...) -> None: ...

class fileRequest(_message.Message):
    __slots__ = ("urlCopy", "fileName", "partitionName", "content")
    URLCOPY_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARTITIONNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    urlCopy: str
    fileName: str
    partitionName: str
    content: bytes
    def __init__(self, urlCopy: _Optional[str] = ..., fileName: _Optional[str] = ..., partitionName: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class fileResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class copyRequest(_message.Message):
    __slots__ = ("fileName", "partitionName", "content")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARTITIONNAME_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    partitionName: str
    content: bytes
    def __init__(self, fileName: _Optional[str] = ..., partitionName: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class copyResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class ResponseSimple(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: bytes
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[bytes] = ...) -> None: ...

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
    __slots__ = ("fileName", "partName")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARTNAME_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    partName: str
    def __init__(self, fileName: _Optional[str] = ..., partName: _Optional[str] = ...) -> None: ...

class readResponse(_message.Message):
    __slots__ = ("status_code", "response")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    response: bytes
    def __init__(self, status_code: _Optional[int] = ..., response: _Optional[bytes] = ...) -> None: ...

class writeRequest(_message.Message):
    __slots__ = ("fileName", "partName", "data")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARTNAME_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    fileName: str
    partName: str
    data: bytes
    def __init__(self, fileName: _Optional[str] = ..., partName: _Optional[str] = ..., data: _Optional[bytes] = ...) -> None: ...

class writeResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class distributeFilesRequest(_message.Message):
    __slots__ = ("urlCopy", "fileName", "partitionName")
    URLCOPY_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    PARTITIONNAME_FIELD_NUMBER: _ClassVar[int]
    urlCopy: str
    fileName: str
    partitionName: str
    def __init__(self, urlCopy: _Optional[str] = ..., fileName: _Optional[str] = ..., partitionName: _Optional[str] = ...) -> None: ...

class distributeFilesResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...
