set(PROTO_BIN   protobin)
set(PROTO_FILES ${PROJECT_SOURCE_DIR}/src/proto/message.proto)

PROTOBUF_GENERATE_CPP(
    PROTO_SRCS 
    PROTO_HDRS 
    ${PROTO_FILES}
)
