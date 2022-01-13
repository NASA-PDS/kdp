import kubernetes
import time

def wait_for_deployment_ready(api, deployment_name, namespace, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(1) # 1s between checks
        response = api.read_namespaced_deployment_status(deployment_name, namespace)
        s = response.status
        if (s.updated_replicas == response.spec.replicas and
                s.replicas == response.spec.replicas and
                s.available_replicas == response.spec.replicas and
                s.observed_generation >= response.metadata.generation):
            return True
        else:
            print(f'[updated_replicas:{s.updated_replicas},replicas:{s.replicas}'
                  ',available_replicas:{s.available_replicas},observed_generation:{s.observed_generation}] waiting...')

    raise RuntimeError(f'Waiting timeout for deployment {deployment_name}')