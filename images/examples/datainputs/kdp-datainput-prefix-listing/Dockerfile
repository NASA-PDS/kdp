FROM kdp-datainput-base:latest
ADD ["entrypoint.sh", "gen_redis_mass_insert.py", "/opt/local/kdp/"]
RUN chmod +x /opt/local/kdp/entrypoint.sh
# install redis so we can use redis-cli
RUN yum install -y http://rpms.remirepo.net/enterprise/remi-release-7.rpm epel-release && \
    yum install -y redis --enablerepo=remi && \
    yum clean all
ENTRYPOINT [ "/opt/local/kdp/entrypoint.sh" ]
