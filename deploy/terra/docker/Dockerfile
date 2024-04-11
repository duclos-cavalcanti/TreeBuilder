FROM ubuntu-ma-base:jammy

ARG BUNDLE

RUN echo $PROJECT_DIR
ADD $BUNDLE /work/project

COPY scripts/entry.sh /entry.sh
RUN chmod +x /entry.sh
