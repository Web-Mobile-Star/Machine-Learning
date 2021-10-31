FROM python:3.8
ARG CI_JOB_TOKEN
ARG GITLAB_API_TOKEN
ENV LIBRARY_PATH=/lib:/usr/lib

COPY . /ml_service
WORKDIR /ml_service

RUN apt-get update && \
  pip install --upgrade pip && \
  pip install poetry && \
  apt-get clean && \
  rm -rf $HOME/.cache

RUN poetry config repositories.gitlab https://gitlab.com/api/v4/projects/9820350/packages/pypi && \
  if [ "$CI_JOB_TOKEN" = "" ] ; \
  then poetry config http-basic.gitlab __token__ ${GITLAB_API_TOKEN} ;\
  else poetry config http-basic.gitlab gitlab-ci-token ${CI_JOB_TOKEN} ; \
  fi && \
  poetry config virtualenvs.path /root/virtualenvs && \
  poetry install --no-root --no-interaction --no-dev && \
  rm -rf $HOME/.cache && \
  rm -rf $HOME/.config/pypoetry/auth.toml

CMD ["poetry", "run", "python", "-m", "ml_service"]
