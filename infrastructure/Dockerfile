FROM alpine:3.19

# Install dependencies
RUN apk add --no-cache \
    bash \
    curl \
    git \
    openssh-client \
    ansible \
    terraform \
    py3-pip \
    sshpass

# Set working directory
WORKDIR /work

# Default to bash
CMD ["/bin/bash"]
