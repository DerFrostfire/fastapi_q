FROM python:3.11
ENV PIP_THREADS=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=100

COPY . .
RUN chmod a+x ci/docker/*.sh

ENTRYPOINT ["ci/docker/app.sh"]
