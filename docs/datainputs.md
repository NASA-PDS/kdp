# DataInputs (TODO/WIP)

A DataInput is how a pipeline gets its input. To support a wide variety of use cases, DataInputs are conceptually different from the pipelines to which they serve data. One example of this use case is when processing occurs in logical "batches" that occur with some regular frequency, perhaps running analytics on server logs at the end of each day. Such a task would be split into two concepts: 

 - A Pipeline for extracting analytics from a single chunk of logs, perhaps from one single machine
 - A DataInput configuration for taking the date (e.g (`2021-01-15`) and dispatching the appropriately sized chunks of work to the pipeline to be worked on

DataInputs, unlike Pipelines, are by default *ephemeral* (`spec.ephemeral: true`). Once they have dispatched all the work, they are deallocated and will no longer take up cluster resources. So in the case of daily analytics, a single DataInput would be created for each day, with no need or concern of overlap with previous days. This consequently means that DataInputs can also be created simultaneously or in bursts, without any concern of missing input data. Each individual DataInput will be handled by the KDP operator, its inputs will be dispatched to its associateed pipeline, and then it will be cleaned up.  

Long-standing DataInputs, such as those that read from a streaming service or external message queue, can be configured using the optional `spec.ephemeral: false` key in the specification. These DataInputs will be installed to the cluster and kept alive until manually removed. Regardless of ephemeral status, DataInput logs & run history are preserved until manually removed. Under the hood, DataInputs are implemented with either a kubernetes `Job` or `Deployment`, depending on the ephemeral setting. The associated resources will remain on the cluster with a `Completed` status, allowing you to investigate logs and maintain a history of which Datainputs have been run in the past. Occasional cleanup may be desired if your use case routinely creates large quantities of DataInputs. Simply delete the DataInput using kubectl, and the KDP operator will perform a complete cleanup for you.

As KDP is designed to support varying use cases, input data to pipelines will vary greatly across projects. To maximize flexibility, the logic behind a DataInput's input dispatching is entirely configurable by the user with a custom container. There are example containers for common use cases such as dispatching an input for every line in a file, directly passing though an S3 object URI, and several others, but if a project's use case is not covered with the examples, writing a container is a simple yet powerful way to get the desired initiation behavior out of a KDP DataInput.

# DataInput Example

An basic example DataInput for a pipeline that accepts S3 prefixes as input might look like the following:

```yaml
apiVersion: kdp.nasa-pds.github.io/v1
kind: DataInput
metadata:
  name: validate-di-ex
spec:
  pipeline:
    id: validate
  data: 
    input_bucket: "example_input_bucket"    # S3 bucket to pull input data from
    output_bucket: "example_output_bucket"  # S3 bucket to push output to
    prefix: "products/00001/"               # S3 prefix to use for both input and output buckets
  image: kdp-datainput-singleinput:latest
```

Note that the DataInput spec consists of three key components:

 - `pipeline.id`
 - `data`
 - `image`

The following sections describe these options in detail and provide examples of their use.

## `pipeline.id`

Each DataInput must map to a specific pipeline deployed to the cluster, which is achieved with the `pipeline.id` field. For example, consider the following pipeline definition:

```yaml
apiVersion: kdp.nasa-pds.github.io/v1
kind: Pipeline
metadata:
  name: validate
spec:
  id: validate
  name: Pipeline for product validation (by directory)
  graph:
    nodes:
      validate-directory:
        image: kdp-node-validate-directory:latest
        command:
          - "/opt/local/kdp/validatedirectory/validatedirectory.py"
      log-validation-summary:
        image: kdp-node-passthrough:latest
        command:
          - "/opt/local/kdp/passthrough.py"
    edges:
      - source: validate-directory
        target: log-validation-summary
```

In this example, the pipeline `id` is `validate`, and it is found in `spec.id` in the pipeline yaml or json definition. For KDP to map a DataInput to the above pipeline, the DataInput's spec **must** include the following:

```yaml
# ...
spec:
  pipeline:
    id: validate
# ...
```

## `data`

The `data` field contains the data that will be json-encoded and fed as input to the provided container. For example, if inputs are to be read from a path in S3, then `data` might look like:

```yaml
data: 
  input_bucket: "example_input_bucket"    # S3 bucket to pull input data from
  output_bucket: "example_output_bucket"  # S3 bucket to push output to
  prefix: "products/00001/"               # S3 prefix to use for both input and output buckets
```

> Note that the keys are not required to be any particular value - we use `input_bucket`, `output_bucket`, and `prefix` here because that's what the `validate-directory` container expects to see in its input.

KDP will take the contents of the `data` object, encode it as JSON, and expose it to the supplied container through the `DATA_JSON` environment variable. In the above example, inspecting `DATA_JSON` in a shell would yield:


```
> echo $DATA_JSON
{"input_bucket": "example_input_bucket", "output_bucket": "example_output_bucket", "prefix": "products/00001/"}
```

Note that `data` is an arbitrary object, and can thus contain nested data:

```yaml
data:
  job:
    path: /path/to/object
    algorithm: ver2
    output: /path/to/output
```

The above would yeild the following in the container:

```
> echo $DATA_JSON
{"job": {"path": "/path/to/object", "algorithm": "ver2", "output": "/path/to/output"}}
```

## `image`

TODO