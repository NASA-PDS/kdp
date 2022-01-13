import os
import kopf
import kubernetes
import yaml
from manifestutil import create_queue_manifests, create_node_manifests, create_datainput_manifests, create_datainput_patch
from utils import wait_for_deployment_ready

@kopf.on.create('kdp.nasa-pds.github.io', 'v1', 'pipelines')
def create_pipeline(spec, name, namespace, logger, **kwargs):
    # when we see a pipeline hit k8s, we want to create the following:
    # - redis work queue (list) for each edge
    # - job for each node

    k8s_core = kubernetes.client.CoreV1Api()
    k8s_apps = kubernetes.client.AppsV1Api()
    k8s_batch = kubernetes.client.BatchV1Api()
    
    # queue manifests
    deployment, service, configmap = create_queue_manifests(spec, name, namespace, logger)
    # logger.info(yaml.dump(configmap))
    kopf.adopt(configmap)
    queue_configmap = k8s_core.create_namespaced_config_map(
        namespace=namespace,
        body=configmap
    )
    logger.info(f"Queue configmap created: {queue_configmap}")
    
    # logger.info(yaml.dump(service))
    kopf.adopt(service)
    queue_service = k8s_core.create_namespaced_service(
        namespace=namespace,
        body=service
    )
    logger.info(f"Queue service created: {queue_service}")

    # logger.info(yaml.dump(deployment))
    kopf.adopt(deployment)
    queue_deployment = k8s_apps.create_namespaced_deployment(
        namespace=namespace,
        body=deployment
    )
    logger.info(f"Queue deployment created: {queue_deployment}")

    names = {
        'queue-deployment-name': queue_deployment.metadata.name,
        'queue-service-name': queue_service.metadata.name,
        'queue-configmap-name': queue_configmap.metadata.name
    }

    # wait for queue ready (max 30 seconds)
    try:
        wait_for_deployment_ready(k8s_apps, queue_deployment.metadata.name, namespace, timeout=30)
    except RuntimeError as e:
        # tell kopf to retry this rollout in 1 minute
        raise kopf.HandlerRetryError("Redis deployment took too long", delay=60)

    # node manifests
    for job in create_node_manifests(spec, name, namespace, logger):
        # logger.info(yaml.dump(job))
        kopf.adopt(job)
        job = k8s_batch.create_namespaced_job(
            namespace=namespace,
            body=job
        )
        logger.info(f"Job created: {job}")

        names.setdefault('job-names', []).append(job.metadata.name)
    
    return names

@kopf.on.update('kdp.nasa-pds.github.io', 'v1', 'pipelines')
def update_pipeline(spec, status, namespace, logger, **kwargs):
    pass

@kopf.on.create('kdp.nasa-pds.github.io', 'v1', 'datainputs')
def create_datainput(spec, name, namespace, logger, **kwargs):
    # when we see a datainput hit k8s, we want to create the following:
    # job / deployment with the given container & inputs

    # get manifest
    ephemeral, manifest = create_datainput_manifests(spec, name, namespace, logger)
    kopf.adopt(manifest)

    info = {}

    # short-lived or long-standing?
    if ephemeral:
        # install as job
        k8s_batch = kubernetes.client.BatchV1Api()
        job = k8s_batch.create_namespaced_job(
            namespace=namespace,
            body=manifest
        )

        logger.info(f"DataInput job created: {job}")

        info = {
            'datainput-type': 'job',
            'datainput-name': job.metadata.name
        }
    else:
        # install as deployment
        k8s_apps = kubernetes.client.AppsV1Api()
        deployment = k8s_apps.create_namespaced_deployment(
            namespace=namespace,
            body=manifest
        )

        logger.info(f"DataInput deployment created: {deployment}")

        info = {
            'datainput-type': 'deployment',
            'datainput-name': deployment.metadata.name
        }

    return info

@kopf.on.update('kdp.nasa-pds.github.io', 'v1', 'datainputs')
def update_datainput(spec, status, namespace, logger, **kwargs):
    '''update datainput container (long-standing deployments only)'''
    di_type = status['create_datainput']['datainput-type']
    di_name = status['create_datainput']['datainput-name']
    image = spec.get('image', None)
    data = spec.get('data', None)
    
    if di_type == 'job':
        raise kopf.PermanentError(f"Cannot update an ephemeral DataInput!")
    if not image and not data:
        raise kopf.PermanentError(f"Cannot update, must specify at least one of: [image, data]")

    di_patch = create_datainput_patch(spec, status, namespace, logger)

    k8s_apps = kubernetes.client.AppsV1Api()
    obj = k8s_apps.patch_namespaced_job(
        namespace=namespace,
        name=di_name,
        body=di_patch,
    )

    logger.info(f"DataInput updated: {obj}")