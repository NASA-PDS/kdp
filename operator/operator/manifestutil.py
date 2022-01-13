import os
import yaml
import kopf
import json

def create_queue_manifests(spec, name, namespace, logger):
    '''generator for k8s manifests for redis'''
    # load deployment template for redis 
    path = os.path.join(os.path.dirname(__file__), 'manifests/queue/deployment.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=f"{name}-redis", label="redis")
    deployment = yaml.safe_load(text)

    # load service template for redis
    path = os.path.join(os.path.dirname(__file__), 'manifests/queue/service.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=f"{name}-redis", label="redis")
    service = yaml.safe_load(text)

    # load configmap template for redis 
    path = os.path.join(os.path.dirname(__file__), 'manifests/queue/health-configmap.yaml')
    tmpl = open(path, 'rt').read()
    text = tmpl.format(name=f"{name}-redis", label="redis")
    configmap = yaml.safe_load(text)

    return (deployment, service, configmap)

def create_node_manifests(spec, name, namespace, logger):
    '''generator for k8s manifests for each node'''
    # load job template for nodes
    path = os.path.join(os.path.dirname(__file__), 'manifests/node/job.yaml')
    tmpl = open(path, 'rt').read()

    graph = spec.get('graph')

    nodes = {}

    # compile incoming & outgoing for each node
    for edge in graph.get('edges'):
        # outgoing
        nodes.setdefault(edge.get('source'), {}).setdefault('outgoing', []).append(edge.get('target'))
        # incoming
        nodes.setdefault(edge.get('target'), {}).setdefault('incoming', []).append(edge.get('source'))

    for node in graph.get('nodes').keys():
        job_name = f"{name}-{node}"
        _node = graph.get('nodes').get(node)
        image = _node.get('image')
        command = _node.get('command')
        pullSecret = _node.get('pullSecret')
        outgoing = json.dumps(nodes.get(node).get('outgoing', []))
        incoming = nodes.get(node).get('incoming', [])
        secrets = graph.get('secrets')
        parallelism = _node.get('parallelism')

        # add external input (pipeline id) to root
        if not incoming:
            incoming.append(name)
        
        incoming = json.dumps(incoming)

        format_args = {
            'name': job_name,
            'container_name': node,
            'container_image': image,
            'queue_name': f'{name}-redis.{namespace}',
            'queue_port': 6379, 
            'input': incoming, 
            'output': outgoing, 
            'pipeline_id': name
        }

        text = tmpl.format(**format_args)
        manifest = yaml.safe_load(text)

        logger.info(manifest['spec']['template']['spec']['containers'][0]['env'])

        # add commands to spec
        if command:
            manifest['spec']['template']['spec']['containers'][0]['args'].extend(command)

        # add imagePullSecrets if present
        if pullSecret:
            manifest['spec']['template']['spec']['imagePullSecrets'] = [{'name': pullSecret}]

        # add envFrom secrets if present
        if secrets:
            for secret in secrets:
                env_from = { 'secretRef': { 'name': secret } }
                manifest['spec']['template']['spec']['containers'][0].setdefault('envFrom', []).append(env_from)

        # add parallelism if present
        if parallelism:
            manifest['spec']['parallelism'] = parallelism

        logger.info(yaml.dump(manifest))

        yield manifest

def create_datainput_manifests(spec, name, namespace, logger):
    '''generator for k8s manifests for each datainput'''
    # first check ephemeral to see which template to load
    ephemeral = spec.get('ephemeral')
    deployment_manifest = os.path.join(os.path.dirname(__file__), 'manifests/datainput/deployment.yaml')
    job_manifest = os.path.join(os.path.dirname(__file__), 'manifests/datainput/job.yaml')
    
    path = job_manifest if ephemeral else deployment_manifest
    tmpl = open(path, 'rt').read()

    # extract info from CRD
    # TODO: limit these names to 63 chars
    job_name = f"{name}-datainput" 
    container_name = f"{name}-datainput-container"
    image = spec.get('image')
    data_json = json.dumps(spec.get('data'))
    pullSecret = spec.get('pullSecret')
    pipeline_id = spec.get('pipeline').get('id')
    queue_hostname = f"{pipeline_id}-redis.{namespace}"
    queue_id = f"{pipeline_id}-work"
    secrets = spec.get('secrets')

    # format the manifest
    format_args = {
        'name': job_name,
        'label': job_name,
        'container_name': container_name,
        'container_image': image,
        'data_json': data_json,
        'queue_hostname': queue_hostname,
        'queue_port': 6379,
        'queue_id': queue_id
    }

    text = tmpl.format(**format_args)
    manifest = yaml.safe_load(text)

    # add imagePullSecrets if present
    if pullSecret:
        manifest['spec']['template']['spec']['imagePullSecrets'] = [{'name': pullSecret}]

    # add envFrom secrets if present
    if secrets:
        for secret in secrets:
            env_from = { 'secretRef': { 'name': secret } }
            manifest['spec']['template']['spec']['containers'][0].setdefault('envFrom', []).append(env_from)

    logger.info(yaml.dump(manifest))

    return (ephemeral, manifest)

def create_datainput_patch(spec, status, namespace, logger):
    '''generate patch object for datainput deployments'''

    di_name = status['create_datainput']['datainput-name']
    image = spec.get('image', None)
    data_json = spec.get('data', None)

    di_patch = {
        'spec': {
            'template': {
                'spec': {
                    'containers': [{
                        'name': di_name + '-container'
                    }]
                }
            }
        }
    }

    # note on imagePullSecrets - we can't update it without deleting the entire
    # resource & redeploying, so we won't support patching to containers
    # that require different auth for now

    # patch image if specified
    if image:
        di_patch['spec']['template']['spec']['containers'][0]['image'] = image

    # patch data if specified
    if data_json:
        env = [{
            'name': 'DATA_JSON',
            'value': json.dumps(data_json)
        }]
        di_patch['spec']['template']['spec']['containers'][0]['env'] = env

    logger.info(yaml.dump(di_patch))

    return di_patch