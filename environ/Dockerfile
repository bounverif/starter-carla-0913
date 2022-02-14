FROM python:3.8-slim

ARG CARLA_RELEASE=0.9.13

RUN groupadd work -g 1000 \
   && useradd -ms /bin/bash carla -g 1000 -u 1000 \
   && printf "carla:carla" | chpasswd \
   && printf "carla ALL= NOPASSWD: ALL\\n" >> /etc/sudoers

USER carla
WORKDIR /home/carla/    

RUN python3 -m pip install --user carla==${CARLA_RELEASE}

COPY . /home/carla/environ/

ENTRYPOINT ["python3", "/home/carla/environ/app.py"]
