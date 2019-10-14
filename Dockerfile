FROM  python:3.7.4-buster

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY . .
COPY ./config.toml /root/.timetracker/config.toml

RUN pip install timetracker-cli

ENTRYPOINT [ "tt" ]

CMD ["show"]
