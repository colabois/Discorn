FROM python:3.8

RUN apt-get update && apt-get install -y\
    rsync \
    openssh-client \
    zip \
    texlive-full

RUN pip install pipenv

CMD ["/bin/bash"]
