FROM ubuntu:latest
LABEL authors="ogabe"

ENTRYPOINT ["top", "-b"]