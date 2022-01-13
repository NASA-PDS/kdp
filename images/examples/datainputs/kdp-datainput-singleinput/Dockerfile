FROM kdp-datainput-base:latest

ADD singleinput.py /opt/local/kdp/

RUN chmod +x /opt/local/kdp/singleinput.py 

ENTRYPOINT [ "/opt/local/kdp/singleinput.py" ]