# step 1: decompress the tar file and put it under /usr/local/openjdk
FROM centos:6 AS base

ENV JAVA_HOME /usr/local/openjdk
ENV PATH $JAVA_HOME/bin:$PATH

ADD . /tmp

RUN mkdir -p $JAVA_HOME && \
	tar --extract --file *jdk*.tar.gz --directory $JAVA_HOME --strip-components 1 && \
	javac -version && \
	java -version

# step 2: copy the previous build content to a new image to reduce image size
FROM centos:6

ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
ENV JAVA_HOME /usr/local/openjdk
ENV PATH $JAVA_HOME/bin:$PATH

COPY --from=base /usr/local/openjdk /usr/local/openjdk

RUN javac -version \
	&& java -version
