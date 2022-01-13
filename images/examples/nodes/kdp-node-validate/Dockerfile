FROM kdp-node-base:latest

# Install some base packages
RUN yum -y install \
           java-1.8.0-openjdk \
           && yum clean all

# Install PDS Validate
RUN mkdir -p /usr/opt/validate && \
    mkdir -p /usr/opt/ldds && \
    curl -LO 'https://github.com/NASA-PDS/validate/releases/download/v2.0.7/validate-2.0.7-bin.tar.gz' && \
    tar -xzf validate-2.0.7-bin.tar.gz -C /usr/opt/validate --strip-components=1 && \
    rm validate-2.0.7-bin.tar.gz

ENV JAVA_HOME=/etc/alternatives/jre \
    VALIDATE_BIN=/usr/opt/validate/bin \
    VALIDATE_LDDS=/usr/opt/ldds