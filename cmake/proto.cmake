set(PROTO_BIN   protobin)
set(PROTO_FILES ${PROJECT_SOURCE_DIR}/lib/proto/message.proto)
set(PROTO_LIBRARY_DIR ${PROJECT_SOURCE_DIR}/lib/proto)

PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS ${PROTO_FILES})
