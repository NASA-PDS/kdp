FROM centos:7.9.2009

RUN yum -y install \
           python3 \
           python3-pip \
           && yum clean all

RUN curl -o /usr/local/bin/mc https://dl.min.io/client/mc/release/linux-amd64/mc \
  && chmod +x /usr/local/bin/mc \
  && pip3 install -Iv minio==7.0.1

ADD ["manager", "entrypoint.sh", "manager/requirements.txt", "/opt/local/kdp/"]

# TODO: push awscli & boto3 to derivative containers
RUN pip3 install -r /opt/local/kdp/requirements.txt && chmod +x /opt/local/kdp/app.py /opt/local/kdp/entrypoint.sh

ENTRYPOINT [ "/opt/local/kdp/entrypoint.sh" ]