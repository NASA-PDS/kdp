# DataInput for a single input

This is the simplest example of an KDP DataInput container. It takes a single string input from the `data.input` field and passes it along to the input queue for the pipeline associated with `spec.pipeline`. An example DataInput CRD is shown below:

```yaml
apiVersion: kdp.nasa-pds.github.io/v1
kind: DataInput
metadata:
  name: inp-02654
spec:
  pipeline:
    id: pipeline-example
  data: 
    input: "s3://some-bucket/some-dir/02654/"
  image: kdp-datainput-singleinput:latest
```