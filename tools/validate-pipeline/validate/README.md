# KDP Pipeline Definition Validation Tool

This tool validates pipeline KDP pipeline definitions to make user error an impossibility when specifying a processing pipeline.

Pipelines are checked against the following criteria:

 - JSON validation
 - Schema validation
 - Content validation
   - No duplicate edges
   - Edges must reference valid nodes
   - Each node must refer to a valid container image
 - Graph validation
   - Only a single root node is allowed
   - Nodes cannot have edges to themselves
   - The graph cannot contain any cycles
   - All nodes must be reachable from the root node
 - Cross-pipeline validation
   - Each pipeline must have a unique `id`

# Usage

```
% python validate-pipeline.py -h                                                                 
usage: validate-pipeline.py [-h] [-s SCHEMA] [-q] pipeline_dir

KDP Pipeline Definition Validation Tool

positional arguments:
  pipeline_dir          Directory containing JSON pipeline definitions

optional arguments:
  -h, --help            show this help message and exit
  -s SCHEMA, --schema SCHEMA
                        JSON schema for pipeline definitions
  -q, --quiet           Suppress all non-error output
```

# Example usage

Given the following example pipeline definition:

```json
{
    "id": "example",
    "name": "Example Pipeline",
    "graph": {
        "nodes": {
            "start": {
                "image": "starting-container-id"
            },
            "middle": {
                "image": "middle-container-id"
            },
            "last": {
                "image": "last-container-id",
                "options": {
                    "config": {
                        "foo": "value",
                        "bar": true
                    }
                }
            }
        },
        "edges": [
            {
                "source": "start",
                "target": "middle"
            },
            {
                "source": "middle",
                "target": "last"
            }
        ]
    }
}
```

The validator will produce the following output:

```
% python validate-pipeline.py -s pipeline.schema.json pipelines
Validating KDP Pipelines
Using options:
  * schema: ../../config/schemas/pipeline.schema.json
  * pipeline_dir: ../../config/pipelines
  * verbose: True

Validating ../../config/pipelines/example-pipeline.json:
Pre-validation:
  * OK: Pipeline is valid JSON
  * OK: Pipeline matches JSON schema
Content validation:
  * OK: No duplicate nodes or edges
  * OK: Each edge references valid nodes
  * TODO: Each node has a valid image
Graph validation:
  * OK: Only one root (start)
  * OK: Nodes do not have edges to themselves
  * OK: No cycles detected
  * OK: All nodes reachable from root
Graph summary:
  * nodes: start, middle, last
  * edges:
    * start -> middle
    * middle -> last

Cross-pipeline validation:
  * OK: All pipeline ids unique
```