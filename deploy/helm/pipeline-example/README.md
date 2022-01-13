# KDP example pipeline (helm) (README TODO/WIP)

This is a runnable example of using helm to maname a KDP pipeline deployment.

**TL;DR**:

```
kubectl create namespace kdp
helm install -n kdp pipeline-example .
<wait for pipeline to come online>
kubectl apply -f ../datainput-example/datainput.yaml
```

## Prerequisites

This example pipeline requires a valid KDP operator deployed to a Kubernetes (K8s) cluster. The K8s cluster can be anywhere from a minikube installation on a laptop to a managed cluster in a cloud services provider such as AWS. `kdp-operator` can be installed with [Helm](https://helm.sh/). See the [readme](../operator/README.md) for more detailed deployment information.

Installation of `kdp-operator` is as simple as:

```
helm install -n kdp-operator kdp-operator ../operator
```

This assumes a `kdp-operator` namespace on your cluster.

## Configuration

Configure the pipeline by overriding the values in `helm/values.yaml`. You can tweak the following values:

 - `node_one.image` and `node_two.image`
   - Use these fields to change the location of the images. For example, if you're running on AWS, the image will need to be pushed to ECR so K8s can access it.
 - `node_one.parallelism` and `node_two.parallelism`
   - Use these fields to change the number of pods K8s will deploy for each pipeline step. Defaults to 64 and 8, respectively.
 - `pipeline.id`
   - This is the ID of the KDP pipeline. Use this to link datainputs to the pipeline. Value is arbitrary but needs to follow K8s naming rules.

## Installing the pipeline to KDP

### Build the helm chart locally

To build the helm chart for the pipeline, run the following command from then `helm/` directory:

```
helm package .
```

This will create `kdp-example-chart-0.1.0.tgz`, which will be used in the next step.

### Install the helm chart

To install this pipeline to KDP, first ensure that you have configured `kubectl` to access your K8s cluster, then run the following command to submit the pipeline to KDP:

*Default installation (parallelism 64/8)*:
```
helm install -n kdp kdp-example kdp-example-chart-0.1.0.tgz
```

*Installation with overrides*:
```
helm install -f /path/to/your/values.yaml -n kdp kdp-example kdp-example-chart-0.1.0.tgz
```

Note that the desired namespace can be changed as well as the helm release name.

This will create the pipeline in the K8s cluster. You'll need to wait for the pipeline to be fully deployed by K8s before moving on to the next step. It might take a moment to fully provision - you can watch it happen live with the following command:

```
kubectl get pods -n kdp -w
```

You will first see a pod with `redis` in its name come up - K8s will wait for it to be ready, then will spin up the rest of the pipeline's resources in quick succession. You should have as many pods per pipeline step as the `parallelism` fields in `values.yaml`.

# Running the pipeline

## Configuring the datainputs

There are two datainputs in this repository:

```
datainputs
├── datainput1.yaml
└── datainput2.yaml
```

Their configuration is contained in the `spec.data` section:

```
data:
  key1: val1
  key2: val2
  key3: val3
```

`key1` - TODO
`key2` - TODO
`key3` - TODO

You can also change the following:

`spec.pipeline.id` - KDP pipeline ID to link to. The default value in this repo should work so long as it wasn't overridden when installing the pipeline via the steps above.
`spec.image` - location of the docker image for this datainput. Will need to change if running somewhere other than AWS.

## Applying the datainputs to the cluster

Run the pipeline by applying any number of datainputs to it - these will take user-provided parameters and use them to submit processing jobs to the KDP pipeline.

The datainputs in this repository can be applied with the following:

```
kubectl apply -f datainputs/<datainput file>.yaml
```

You may apply multiple datainputs to the pipeline.

> *Note that processing will begin once the above command is run successfully.*

# Resource tuning

You may wish to update the resources available to the pipeline. This can be accomplished by editing the `spec.parallelism` field for a given pipeline job.  

First you need to identify which job needs to be patched. Run the following:

```
kubectl get jobs -n <your namepsace>
```

To get a listing of job names in your pipeline namespace. Identify the one that corresponds to the step you wish to change and note it for later.

Now prepare a file `patch.yaml`:

```
spec:
  parallelism: <desired number of pods>
```

Now update the job with the patch:

```
kubectl patch job <job name> -n <your namespace> --patch "$(cat patch.yaml)"
```