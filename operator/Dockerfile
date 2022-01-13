FROM python:3.9
ADD ["requirements.txt", "operator", "/src/"]
RUN pip install -r /src/requirements.txt
CMD kopf run /src/operator.py --verbose