FROM centos:7.9.2009

RUN yum -y install \
           python3 \
           python3-pip \
           nc \
           && yum clean all

RUN curl -o /usr/local/bin/mc https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x /usr/local/bin/mc

RUN pip3 install -Iv redis==3.5.3 minio==7.0.1 awscli==1.19.71 boto3==1.18.5
