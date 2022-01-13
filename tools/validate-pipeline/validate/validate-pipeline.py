import json
import os
import re
import argparse
from graphutil import tarjan, from_edges, bfs
from jsonschema import validate, ValidationError

# Command line options
parser = argparse.ArgumentParser(description='KDP Pipeline Definition Validation Tool')
parser.add_argument('-s', '--schema', dest='schema', action='store', default='../resources/schemas/pipeline.schema.json',
                    help='JSON schema for pipeline definitions')
parser.add_argument('pipeline_dir', action='store',
                    help='Directory containing JSON pipeline definitions')
parser.add_argument('-q', '--quiet', dest='verbose', action='store_false',
                    help='Suppress all non-error output')

args = parser.parse_args()
verbose = args.verbose

if verbose:
    print("Validating KDP Pipelines")
    print("Using options:")
    for arg in vars(args):
        print(f"  * {arg}: {str(getattr(args, arg))}")
    print()

# Validating a pipeline
#  - JSON validation
#  - Schema validation
#  - Content validation
#    - No duplicate edges
#    - Edges must reference a valid node
#    - Each node has a valid image
#  - Graph validation
#    - Single root
#    - Nodes cannot have an edge to themselves
#    - No cycles
#    - All nodes reachable from root
#  - Cross-pipeline validation
#    - All unique pipeline ids

# Load the schemas 
# Use os.listdir over glob so we can match both *.json and *.JSON
pipelines = [f for f in os.listdir(args.pipeline_dir) if re.match(r'.*\.(json|JSON)', f)]

with open(args.schema) as s:
    schema = json.load(s)

    # Validate each pipeline definition via the steps above
    pipeline_ids = [] # keep track of ids
    for p in pipelines:
        with open(os.path.join(args.pipeline_dir, p)) as f:
            if verbose: 
                print(f"Validating {os.path.join(args.pipeline_dir, p)}:")

            indent = 2 # output padding

            # Pre-validation
            section = 'Pre-validation'
            if verbose: 
                print(f"{section}:")

            # JSON format validation
            try:
                pipeline = json.load(f)
                if verbose: 
                    print(f"{' ' * indent}* OK: Pipeline is valid JSON")
            except ValueError:
                print(f"{' ' * indent}* ERROR ({section}): Pipeline '{p}' is not valid JSON!")
                raise

            # JSON schema validation
            try:
                validate(instance=pipeline, schema=schema)
                if verbose: 
                    print(f"{' ' * indent}* OK: Pipeline matches JSON schema")
            except ValidationError:
                print(f"{' ' * indent}* ERROR: ({section}): Pipeline '{p}' does not match JSON schema! Details:")
                raise

            # Add pipeline id to list
            pipeline_ids.append(pipeline['id'])

            # Load in the nodes & edges
            nodes = pipeline['graph']['nodes']
            edges = pipeline['graph']['edges']

            # Content validation
            section = 'Content validation'
            if verbose: 
                print(f"{section}:")

            # No duplicate edges

            if len(edges) != len(set([f"{edge['source']}-{edge['target']}" for edge in edges])):
                print(f"{' ' * indent}* ERROR: ({section}): Duplicate edge detected!")
                raise SystemExit # exit on duplicate edges
            if verbose: 
                print(f"{' ' * indent}* OK: No duplicate nodes or edges")

            # Edges must reference a node
            for edge in edges:
                if edge['source'] not in nodes:
                    print(f"{' ' * indent}* ERROR: ({section}): Edge references invalid node in edge.source ({edge['source']}): {edge}")
                    raise SystemExit # exit on invalid edge
                if edge['target'] not in nodes:
                    print(f"{' ' * indent}* ERROR: ({section}): Edge references invalid node in edge.target ({edge['target']}): {edge}")
                    raise SystemExit # exit on invalid edge
            if verbose: 
                print(f"{' ' * indent}* OK: Each edge references valid nodes")

            # TODO: Each node has a valid image
            if verbose: 
                print(f"{' ' * indent}* TODO: Each node has a valid image")

            # Graph validation
            section = 'Graph validation'
            if verbose: 
                print(f"{section}:")

            # Single root
            # see which node has no target
            hasIncoming = set()
            for edge in edges:
                hasIncoming.add(edge['target'])
            root = [n for n in nodes if n not in hasIncoming]
            if len(root) == 0:
                print(f"{' ' * indent}* ERROR: ({section}): No root node could be identified!")
                raise SystemExit # exit on no root
            if len(root) > 1:
                print(f"{' ' * indent}* ERROR: ({section}): More than one root node identified: {root}")
                raise SystemExit # exit on more than one root
            if verbose: 
                print(f"{' ' * indent}* OK: Only one root ({root[0]})")

            # Nodes cannot have an edge to themselves
            for edge in edges:
                if edge['source'] == edge['target']:
                    print(f"{' ' * indent}* ERROR: ({section}): Node has edge to itself: {edge}")
                    raise SystemExit # exit on invalid edge
            if verbose: 
                print(f"{' ' * indent}* OK: Nodes do not have edges to themselves")

            # No cycles
            edges_as_list = [(edge['source'], edge['target']) for edge in edges]

            # Get the strongly connected components
            sccs = [g for g in tarjan(from_edges(edges_as_list)) if len(g) > 1]
            if sccs:
                print(f"{' ' * indent}* ERROR: ({section}): One or more cycles detected in pipeline graph: {sccs}")
                raise SystemExit # exit on cycles
            if verbose: 
                print(f"{' ' * indent}* OK: No cycles detected")

            # All nodes reachable from root
            # We are guaranteed to be dealing with a DAG at this point
            # TODO: This never gets raised because an unreachable node would either:
            #    * be caught by the multiple root nodes check above; or
            #    * be caught by the cycle check above
            reachable = bfs(from_edges(edges_as_list), root[0])
            unreachable = set(list(nodes.keys())) - set(reachable)
            if len(unreachable) > 0:
                print(f"{' ' * indent}* ERROR: ({section}): One or more nodes unreachable from root: {list(unreachable)}")
                raise SystemExit # exit on unreachable
            if verbose: 
                print(f"{' ' * indent}* OK: All nodes reachable from root")

            if verbose:
                print(f"Graph summary:")
                print(f"{' ' * indent}* nodes: {', '.join(nodes)}")
                print(f"{' ' * indent}* edges:")
                for edge in edges:
                    print(f"{' ' * indent * 2}* {edge['source']} -> {edge['target']}")

        # Blank line in between pipeline validations
        if verbose:
            print()
    
    # Cross-pipeline validation
    section = 'Cross-pipeline validation'
    if verbose: 
        print(f"{section}:")

    # Make sure pipeline ids are unique
    if len(set(pipeline_ids)) != len(pipeline_ids):
        # find the dupe
        seen = {}
        for id in pipeline_ids:
            if id not in seen:
                seen[id] = id
            else:
                print(f"{' ' * indent}* ERROR: ({section}): Duplicate pipeline id: {id}")
                raise SystemExit # exit on duplicate pipeline ids
    if verbose: 
        print(f"{' ' * indent}* OK: All pipeline ids unique")