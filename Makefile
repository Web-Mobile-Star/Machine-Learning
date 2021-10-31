AWS_DEFAULT_REGION?=eu-central-1
IMAGE_REPO=your_repo_uri
FILES := $(wildcard *.py)

format: $(FILES)
	poetry run black .

flake8: $(FILES) 
	poetry run flake8 .

mypy: $(FILES)
	poetry run mypy --ignore-missing-imports --python-version 3.8 --follow-imports=normal --show-column-numbers .

check: flake8 mypy

test: $(FILES)
	poetry run pytest

image-uri:
    ifeq ($(origin CI_JOB_TOKEN), undefined)
        export IMAGE_URI:=$(IMAGE_REPO):$(TAG)
    else
        IS_MASTER_OR_DEVELOP_COMMIT=$(shell [[ $CI_COMMIT_REF_NAME == "master" || $CI_COMMIT_REF_NAME == "develop" ]])
        ifeq ($(IS_MASTER_OR_DEVELOP_COMMIT), 1)
            export IMAGE_URI:=$(IMAGE_REPO):$(CI_COMMIT_REF_NAME)-$(TAG)
        else 
            export IMAGE_URI:=$(IMAGE_REPO):$(TAG)
        endif
    endif

build: image-uri
    ifeq ($(origin CI_JOB_TOKEN), undefined)
		docker build -t $(IMAGE_URI) --build-arg GITLAB_API_TOKEN=$(GITLAB_API_TOKEN) .
    else
		docker build -t $(IMAGE_URI) --build-arg CI_JOB_TOKEN=$(CI_JOB_TOKEN) .
    endif

docker-push: build
	$$(aws ecr get-login --no-include-email --region $(AWS_DEFAULT_REGION))
	docker push $(IMAGE_URI)
	echo "Uncompressed image size $$(docker images $(IMAGE_URI) --format='{{.Size}}') (compressed about 3x smaller)"

all: format check test docker-push