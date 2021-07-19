FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && \
    apt-get autoclean && \
    apt-get install -y --no-install-recommends \
        qtbase5-dev-tools \
        xvfb \
        libegl1-mesa \
        x11-xserver-utils \
        libxkbcommon-x11-0 \
        x11-utils && \
    apt-get clean && \
    rm -rf /var/cache/apk/* && \
    python -m pip install --no-cache-dir --upgrade pip && \
    pip3 install -r requirements.txt && \
    apt-get purge -y build-essential && \
    apt-get purge -y cmake

COPY . .

CMD [ "python3", "main.py"]