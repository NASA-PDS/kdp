# kdp-operator
Helm chart for the KDP Operator. This chart will install the the operator to your cluster & create the necessary Custom Resource Definitions (CRDs) & Role-Based Access Control (RBAC) to get the KDP operator up-and-running with a single helm install.

We recommend using helm to manage the operator on your cluster, as it is a nice way to get the operator configured properly without having to manage your own RBAC & CRDs.

# TL;DR

```
kubectl create namespace kdp-operator
helm install kdp-operator . -n kdp-operator
```

# Prerequisites

 - Helm 
 - `kubectl` [configured to a cluster](https://kubernetes.io/docs/tasks/tools/#kubectl)

Refer to the [getting started guide](https://helm.sh/docs/intro/quickstart/) to get helm set up on your machine.

# Using this chart

## Configuration

Default configuration is provided in `values.yaml`, but you can override values by either providing a yaml values file, or by setting the values individually at install.

## Values TODO