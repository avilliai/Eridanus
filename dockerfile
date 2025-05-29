FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim AS builder

RUN set -eux; \
    codename="$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2)"; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian $codename main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian $codename-updates main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security $codename-security main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        git \
        build-essential; \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -; \
    apt-get install -y --no-install-recommends nodejs; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /build/requirements.txt
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install \
        -r /build/requirements.txt \
        PyJWT \
        brotli \
        qrcode \
        qrcode_terminal \
        flask_sock

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.11-slim

RUN set -eux; \
    codename="$(grep VERSION_CODENAME /etc/os-release | cut -d= -f2)"; \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian $codename main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian $codename-updates main contrib non-free non-free-firmware\n\
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security $codename-security main contrib non-free non-free-firmware" > /etc/apt/sources.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        ffmpeg \
        libjpeg-dev \
        zlib1g-dev \
        libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && npm cache clean --force

COPY --from=builder /install /usr/local

COPY . /app/Eridanus
RUN sed -i 's|ws://127.0.0.1:3001|ws://napcat:3001|g' /app/Eridanus/run/common_config/basic_config.yaml

WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

EXPOSE 5007
CMD ["python", "Eridanus/launch.py"]