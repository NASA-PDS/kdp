# Building KDP

While each core KDP component can be built individually, it is much simpler to use the project-level Makefile contained in this folder to build everything.  

## TL;DR

Local build only:

```
make build-all
```

Build & push to container registry:

```
make release-all DOCKER_REPO="your registry here"
```

Build & push to AWS ECR:

```
make release-all-aws \
  DOCKER_REPO="ECR repository here" \
  AWS_CLI_PROFILE="your awscli profile" \
  AWS_CLI_REGION="your awscli region"
```

## Build setup explained

The build setup of KDP looks like the following:

```
kdp
├── build
│   ├── Makefile
│   └── README.md <-- THIS FILE
├── images
│   ├── base
│   │   └── <image>
│   │       └── Makefile
│   └── examples
│       ├── datainputs
│       │   └── <datainput>
│       │       └── Makefile
│       └── nodes
│           └── <node>
│               └── Makefile
└── operator
    └── Makefile
```

The top-level Makefile is `build/Makefile`, in this directory. Each other Makefile in this repository supports identical targets, which makes building & pushing images simple. The top-level Makefile also supports being more granular in your builds - you can choose to only build KDP's core components, for example. This saves time as some of the examples take a few minutes to build depending on your network speed.  

The full annotated list of build targets can be found with `make help`, or simply `make`:

```
help                           This help message
make-all                       Run makefiles for all core KDP components and examples. 
                               Define `TARGET` with `make TARGET="<build|publish|etc>" make-all`
make-core                      Run makefiles for all core KDP components.
                               Define `TARGET` with `make TARGET="<build|publish|etc>" make-core`
make-examples                  Run makefiles for all KDP example components.
                               Define `TARGET` with `make TARGET="<build|public|etc>" make-examples`
build-all                      Build all KDP images and examples
build-core                     Build all KDP core images
build-examples                 Build all KDP example images
publish-all                    Publish all KDP images and examples to `DOCKER_REPO` (must already be built)
publish-core                   Publish all KDP core images to `DOCKER_REPO` (must already be built)
publish-examples               Publish all KDP example images to `DOCKER_REPO` (must already be built)
publish-all-aws                Publish all KDP images and examples to AWS ECR (must already be built)
publish-core-aws               Publish all KDP core images to AWS ECR (must already be built)
publish-examples-aws           Publish all KDP example images to AWS ECR (must already be built)
release-all                    Build & publish all KDP images and examples to `DOCKER_REPO`
release-core                   Build & publish all KDP core images to `DOCKER_REPO`
release-examples               Build & publish all KDP example images to `DOCKER_REPO`
release-all-aws                Build & publish all KDP images and examples to AWS ECR
release-core-aws               Build & publish all KDP core images to AWS ECR
release-examples-aws           Build & publish all KDP example images to AWS ECR
version                        Get KDP image versions
version-core                   Get KDP core image versions
version-examples               Get KDP example image versions
```

> Note that each of the `publish-*` targets assume that images have already been locally built.