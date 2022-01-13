# KDP: Kubernetes does pipelines

KDP is a framework that makes it simple to orchestrate highly performant data processing pipelines. We say *orchestrate* with purpose: KDP leverages the Kubernetes [operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) to create a custom extension of the Kubernetes API. This means that KDP benefits from the advantages of Kubernetes, and that it doesn't actually have to deal with conainer orchestration, lifecycle management, concurrency, etc. That's all up to Kubernetes, and we like it that way.

# Getting Started

KDP has a lot of moving parts, so it will be useful to outline some key concepts that will come up a lot:

TODO: more docs