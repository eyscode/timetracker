FROM  python:3.7.4-buster

RUN mkdir /usr/src/app

WORKDIR /usr/src/app

COPY . .
RUN pip install timetracker-cli

COPY ./config.toml /root/.timetracker/config.toml

ENTRYPOINT [ "tt" ]

CMD ["show"]
