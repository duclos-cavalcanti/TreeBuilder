FROM ubuntu-base:jammy

RUN echo $PROJECT_DIR
ADD project.tar.gz /work/project

COPY scripts/entry.sh /entry.sh
RUN chmod +x /entry.sh
