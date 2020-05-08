# step 1: decompress the tar file and put it under /usr/local/openjdk
FROM ubuntu:18.04 AS base

ENV JAVA_HOME /usr/local/openjdk
ENV PATH $JAVA_HOME/bin:$PATH

ADD . /

RUN mkdir -p $JAVA_HOME && \
	tar --extract --file *jdk*.tar.gz --directory $JAVA_HOME --strip-components 1 && \
	javac -version && \
	java -version

# step 2: copy the previous build content to a new image to reduce image size
FROM ubuntu:18.04

ENV JAVA_HOME /usr/local/openjdk
ENV PATH $JAVA_HOME/bin:$PATH

RUN apt-get update && \
	apt-get install -y --no-install-recommends \
	curl \
	ca-certificates \
	fontconfig \
	locales && \
	echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && \
	locale-gen en_US.UTF-8 && \
	rm -rf /var/lib/apt/lists/*

COPY --from=base /usr/local/openjdk /usr/local/openjdk
