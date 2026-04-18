FROM alpine:3.20

RUN apk add --no-cache bash curl openssh-client sshpass

WORKDIR /workspace

CMD ["sleep", "infinity"]
