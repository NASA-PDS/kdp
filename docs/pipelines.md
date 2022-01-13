# Pipelines TODO/WIP

Note that the names of nodes *must* follow k8s DNS rules (DNS-1123)

From k8s docs:
> lower case alphanumeric characters, '-' or '.', and must start and end with an alphanumeric character (e.g. 'example.com', regex used for validation is `[a-z0-9]([-a-z0-9]*[a-z0-9])?(\\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*`)

Make sure to add imagePullSecrets for each image, if necessary. Will need to install in your cluster.

The `graph.secrets` key is a list of kubernetes secrets you wish to expose to each node in the cluster. This should contain keys to deal with S3 access, external streams, etc. Note: kubernetes secrets can contain multiple key/value pairs. Exposing a secret to your KDP nodes in this manner exposes *all* of the key/value pairs in the secret to each pod in the pipeline.

Given the secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mc-config
data:
  MC_URL: localhost:9000
  MC_ACCESS_KEY: ABC
  MC_SECRET_KEY: abcdefg123456
```

And the following `graph.secrets` entry in the pipeline configuration:

```yaml
secrets:
  - mc-config
```

Each pod will have the following entries:

```
> echo $MC_URL
localhost:9000
> echo $MC_ACCESS_KEY
ABC
> echo $MC_SECRET_KEY
abcdefg123456
```

A simple generic secret such as the one above can be created with the command:

```
kubectl create secret generic mc-config \
  --from-literal=MC_URL='localhost:9000' \
  --from-literal=MC_ACCESS_KEY=ABC \
  --from-literal=MC_SECRET_KEY='abcdefg123456'
```

# Pipeline work queue structure (Maybe move to manager documentation)

KDP defines a work queue for each edge in a pipeline definition. Consider the following pipeline definition:

```
id: queue-example
name: Queue Example Pipeline
graph:
  nodes:
    start:
      image: starting-container-id
    last:
      image: last-container-id
  edges:
    - source: start
      target: last
```

In this case, KDP defines a work queue `start-last-work` that operates in a First-In-First-Out (FIFO) manner, and a 'claimed' list `start-last-claimed`. These two structures are used as follows:

 - When `start` finishes a task and generates its output, it `PUSH`es the output to `start-last-work`. It does this as fast as it can perform work.
 - When `last` is ready for input, it `POP`s from `start-last-work`, and `PUSH`es the result to `start-last-claimed` while also keeping a local copy, which it supplies as input to its container. 
 - When `last` is finished performing its work, it deletes the entry from `start-last-claimed` before posting its output to the next queue down the line (if there are any).
 - `start-last-claimed` is periodically checked for items that have been there too long (TODO CONFIG VALUE), or that have been put there by instances of `last` that are no longer alive. If any are found, it `POP`s them from `start-last-claimed` and `PUSH`es them to `start-last-work`, so that they can be reprocessed.

 For external inputs to the system, the queue `<pipeline_id>-work` is created. This is a special input queue for the starting node of the pipeline. 
 
 > Note: To ensure that you have no naming conflicts with this queue, do not use your pipeline id as the id for any of your nodes.