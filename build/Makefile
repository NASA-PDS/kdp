# makefile heavily inspired by: https://gist.github.com/mpneuried/0594963ad38e68917ef189b4e6a269db

# CONFIG VALUES
# can also be passed when calling make: `make DOCKER_REPO="repo name" AWS_CLI_PROFILE="profile" <...> build-all`
DOCKER_REPO ?=# fill this in if you want to publish to a remote container registry

# optional AWS config. define if you wish to publish using AWS ECR
AWS_CLI_PROFILE ?=
AWS_CLI_REGION ?=

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## This help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

# BUILD TARGETS

make-all: make-core make-examples ## Run makefiles for all core KDP components and examples. Define `TARGET` with `make TARGET="<build|publish|etc>" make-all`

make-core: ## Run makefiles for all core KDP components. Define `TARGET` with `make TARGET="<build|publish|etc>" make-core`
	$(MAKE) -C ../operator $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/base/kdp-datainput-base $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/base/kdp-node-base $(CMD_ARGS) $(TARGET)

make-examples: ## Run makefiles for all KDP example components. Define `TARGET` with `make TARGET="<build|public|etc>" make-examples`
	$(MAKE) -C ../images/examples/datainputs/kdp-datainput-prefix-listing $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/examples/datainputs/kdp-datainput-singleinput $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/examples/nodes/kdp-node-passthrough $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/examples/nodes/kdp-node-validate $(CMD_ARGS) $(TARGET)
	$(MAKE) -C ../images/examples/nodes/kdp-node-validate-directory $(CMD_ARGS) $(TARGET)

# BUILD
build-all: TARGET=build
build-all: make-all ## Build all KDP images and examples

build-core: TARGET=build
build-core: make-core ## Build all KDP core images

build-examples: TARGET=build
build-examples: make-examples ## Build all KDP example images

# PUBLISH
publish-all: TARGET=publish
publish-all: make-all ## Publish all KDP images and examples to `DOCKER_REPO` (must already be built)

publish-core: TARGET=publish
publish-core: make-core ## Publish all KDP core images to `DOCKER_REPO` (must already be built)

publish-examples: TARGET=publish
publish-examples: make-examples ## Publish all KDP example images to `DOCKER_REPO` (must already be built)

# PUBLISH w/ AWS
publish-all-aws: TARGET=publish-aws
publish-all-aws: make-all ## Publish all KDP images and examples to AWS ECR (must already be built)

publish-core-aws: TARGET=publish-aws
publish-core-aws: make-core ## Publish all KDP core images to AWS ECR (must already be built)

publish-examples-aws: TARGET=publish-aws
publish-examples-aws: make-examples ## Publish all KDP example images to AWS ECR (must already be built)

# RELEASE
release-all: TARGET=release
release-all: make-all ## Build & publish all KDP images and examples to `DOCKER_REPO`

release-core: TARGET=release
release-core: make-core ## Build & publish all KDP core images to `DOCKER_REPO`

release-examples: TARGET=release
release-examples: make-examples ## Build & publish all KDP example images to `DOCKER_REPO`

# RELEASE w/ AWS
release-all-aws: TARGET=release-aws
release-all-aws: make-all ## Build & publish all KDP images and examples to AWS ECR

release-core-aws: TARGET=release-aws
release-core-aws: make-core ## Build & publish all KDP core images to AWS ECR

release-examples-aws: TARGET=release-aws
release-examples-aws: make-examples ## Build & publish all KDP example images to AWS ECR


# VERSION TARGETS
version: version-core version-examples ## Get KDP image versions

version-core: ## Get KDP core image versions
	@printf "CORE:\nkdp-operator: "
	@eval $(MAKE) -C ../operator $(CMD_ARGS) version
	@printf "kdp-datainput-base: "
	@eval $(MAKE) -C ../images/base/kdp-datainput-base $(CMD_ARGS) version
	@printf "kdp-node-base: "
	@eval $(MAKE) -C ../images/base/kdp-node-base $(CMD_ARGS) version

version-examples: ## Get KDP example image versions
	@printf "EXAMPLES:\nkdp-datainput-prefix-listing: "
	@eval $(MAKE) -C ../images/examples/datainputs/kdp-datainput-prefix-listing $(CMD_ARGS) version
	@printf "kdp-datainput-singleinput: "
	@eval $(MAKE) -C ../images/examples/datainputs/kdp-datainput-singleinput $(CMD_ARGS) version
	@printf "kdp-node-passthrough: "
	@eval $(MAKE) -C ../images/examples/nodes/kdp-node-passthrough $(CMD_ARGS) version
	@printf "kdp-node-validate: "
	@eval $(MAKE) -C ../images/examples/nodes/kdp-node-validate $(CMD_ARGS) version
	@printf "kdp-node-validate-directory: "
	@eval $(MAKE) -C ../images/examples/nodes/kdp-node-validate-directory $(CMD_ARGS) version

# HELPERS

# generate make config args if defined
CMD_ARGS =
ifdef DOCKER_REPO
CMD_ARGS += "DOCKER_REPO=\"$(DOCKER_REPO)\""
endif
ifdef AWS_CLI_PROFILE
CMD_ARGS += " AWS_CLI_PROFILE=\"$(AWS_CLI_PROFILE)\""
endif
ifdef AWS_CLI_REGION
CMD_ARGS += " AWS_CLI_REGION=\"$(AWS_CLI_REGION)\""
endif
