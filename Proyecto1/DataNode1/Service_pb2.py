# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: Service.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rService.proto\x12\x08sendfile\"\x1b\n\x07Request\x12\x10\n\x08resource\x18\x02 \x01(\x0c\"1\n\x08Response\x12\x13\n\x0bstatus_code\x18\x01 \x01(\x05\x12\x10\n\x08response\x18\x02 \x01(\t\"!\n\rRequestSimple\x12\x10\n\x08resource\x18\x03 \x01(\t\"7\n\x0eResponseSimple\x12\x13\n\x0bstatus_code\x18\x04 \x01(\x05\x12\x10\n\x08response\x18\x03 \x01(\x0c\"-\n\x0bopenRequest\x12\x10\n\x08\x66ileName\x18\x05 \x01(\t\x12\x0c\n\x04mode\x18\x06 \x01(\t\"5\n\x0copenResponse\x12\x13\n\x0bstatus_code\x18\t \x01(\x05\x12\x10\n\x08response\x18\x05 \x01(\t\"\x1f\n\x0breadRequest\x12\x10\n\x08\x66ileName\x18\x07 \x01(\t\"5\n\x0creadResponse\x12\x13\n\x0bstatus_code\x18\n \x01(\x05\x12\x10\n\x08response\x18\x08 \x01(\x0c\"@\n\x0cwriteRequest\x12\x10\n\x08\x66ileName\x18\x0b \x01(\t\x12\x10\n\x08partName\x18\x0c \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\r \x01(\x0c\"$\n\rwriteResponse\x12\x13\n\x0bstatus_code\x18\x0e \x01(\x05\x32\xc1\x02\n\x0eProductService\x12<\n\x0f\x63lientStreaming\x12\x11.sendfile.Request\x1a\x12.sendfile.Response\"\x00(\x01\x12\x43\n\x0c\x63lientSingle\x12\x17.sendfile.RequestSimple\x1a\x18.sendfile.ResponseSimple\"\x00\x12\x37\n\x04open\x12\x15.sendfile.openRequest\x1a\x16.sendfile.openResponse\"\x00\x12\x37\n\x04read\x12\x15.sendfile.readRequest\x1a\x16.sendfile.readResponse\"\x00\x12:\n\x05write\x12\x16.sendfile.writeRequest\x1a\x17.sendfile.writeResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'Service_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_REQUEST']._serialized_start=27
  _globals['_REQUEST']._serialized_end=54
  _globals['_RESPONSE']._serialized_start=56
  _globals['_RESPONSE']._serialized_end=105
  _globals['_REQUESTSIMPLE']._serialized_start=107
  _globals['_REQUESTSIMPLE']._serialized_end=140
  _globals['_RESPONSESIMPLE']._serialized_start=142
  _globals['_RESPONSESIMPLE']._serialized_end=197
  _globals['_OPENREQUEST']._serialized_start=199
  _globals['_OPENREQUEST']._serialized_end=244
  _globals['_OPENRESPONSE']._serialized_start=246
  _globals['_OPENRESPONSE']._serialized_end=299
  _globals['_READREQUEST']._serialized_start=301
  _globals['_READREQUEST']._serialized_end=332
  _globals['_READRESPONSE']._serialized_start=334
  _globals['_READRESPONSE']._serialized_end=387
  _globals['_WRITEREQUEST']._serialized_start=389
  _globals['_WRITEREQUEST']._serialized_end=453
  _globals['_WRITERESPONSE']._serialized_start=455
  _globals['_WRITERESPONSE']._serialized_end=491
  _globals['_PRODUCTSERVICE']._serialized_start=494
  _globals['_PRODUCTSERVICE']._serialized_end=815
# @@protoc_insertion_point(module_scope)
