FROM continuumio/anaconda3

MAINTAINER orange "lanzhizhuxia@gmail.com"

# apt-get换成清华源
RUN sed -i "s@/archive.ubuntu.com/@/mirrors.tuna.tsinghua.edu.cn/@g" /etc/apt/sources.list \
    && rm -Rf /var/lib/apt/lists/* \
    && apt-get update

# Install basic dependencies
RUN apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        wget \
        python3-dev \
        python3-pip


COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

ENTRYPOINT [ "python3" ]

CMD [ "app/app.py" ]