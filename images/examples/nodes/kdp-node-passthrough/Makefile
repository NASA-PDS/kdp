# makefile heavily inspired by: https://gist.github.com/mpneuried/0594963ad38e68917ef189b4e6a269db

# get the version
VERSION=$(shell cat VERSION)
APP_NAME=kdp-node-passthrough

# CONFIG VALUES
# can also be passed when calling make: `make DOCKER_REPO="repo name" AWS_CLI_PROFILE="profile" <...> build`
DOCKER_REPO ?= # fill this in if you want to publish to a remote container registry

# optional AWS config. define if you wish to publish using AWS ECR
AWS_CLI_PROFILE ?=
AWS_CLI_REGION ?=


# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help version

help: ## This help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# Build the container
build: ## Build the container
	docker build -t $(APP_NAME) .

build-nc: ## Build the container without caching
	docker build --no-cache -t $(APP_NAME) .

release: build-nc publish ## Make a release by building and publishing the `{version}` and `latest` tagged containers to `DOCKER_REPO`

release-aws: build-nc publish-aws ## Make a release by building a publishing the `{version}` and `latest` tagged containers to ECR

# Docker publish
publish-aws: aws-login publish-latest publish-version ## Publish the `{version}` and `latest` tagged containers to ECR using AWSCLI login

publish: publish-latest publish-version ## Publish the `{version}` and `latest` tagged containers to `DOCKER_REPO`

publish-latest: tag-latest ## Publish the `latest` taged container to `DOCKER_REPO`
ifdef DOCKER_REPO
	@echo 'publish latest to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)/$(APP_NAME):latest
else
	$(error must define `DOCKER_REPO`!)
endif

publish-version: tag-version ## Publish the `{version}` taged container to `DOCKER_REPO`
ifdef DOCKER_REPO
	@echo 'publish $(VERSION) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO)/$(APP_NAME):$(VERSION)
else
	$(error must define `DOCKER_REPO`!)
endif

# Docker tagging
tag: tag-latest tag-version ## Generate container tags for the `{version}` and `latest` tags

tag-latest: ## Generate container `latest` tag
	@echo 'create tag latest'
ifdef DOCKER_REPO
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):latest
else
	docker tag $(APP_NAME) $(APP_NAME):latest
endif

tag-version: ## Generate container `{version}` tag
	@echo 'create tag $(VERSION)'
ifdef DOCKER_REPO
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):$(VERSION)
else
	docker tag $(APP_NAME) $(APP_NAME):$(VERSION)
endif

# HELPERS

# generate script to login to aws docker repo
CMD_REPOLOGIN := "eval $$\( aws ecr"
ifdef AWS_CLI_PROFILE
CMD_REPOLOGIN += " --profile $(AWS_CLI_PROFILE)"
endif
ifdef AWS_CLI_REGION
CMD_REPOLOGIN += " --region $(AWS_CLI_REGION)"
endif
CMD_REPOLOGIN += " get-login --no-include-email \)"

# login to AWS-ECR
aws-login: ## Auto login to AWS-ECR using aws-cli
ifndef DOCKER_REPO
	$(error must define `DOCKER_REPO`!)
endif
ifndef AWS_CLI_REGION
	$(error must define `AWS_CLI_REGION`!)
endif
ifndef AWS_CLI_PROFILE
	$(error must define `AWS_CLI_PROFILE`!)
endif
	@eval $(CMD_REPOLOGIN)

version: ## Output the current version
	@echo $(VERSION)