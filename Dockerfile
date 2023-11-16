FROM python:3.11.6-slim

ENV HOME "/root"
ENV APP_HOME "$HOME/app"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install poetry
ENV PATH "$HOME/.local/bin:$PATH"
RUN apt-get update && apt-get install --no-install-recommends -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get install -y default-libmysqlclient-dev build-essential && \
    poetry config virtualenvs.create false

# RUN apt-get install -y default-libmysqlclient-dev build-essential 

# install python packages
COPY pyproject.toml poetry.lock $APP_HOME/
RUN poetry install --without=develop --no-root

# install app
COPY ./backend $APP_HOME
RUN poetry install --only-root

# run app
CMD python manage.py runserver --settings=config.settings.production
