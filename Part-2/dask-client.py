from dask_kubernetes.operator import make_worker_spec, make_scheduler_spec

def dask_make_cluster_spec(
    name,
    image="ghcr.io/dask/dask:latest",
    n_workers=None,
    worker_resources=None,
    scheduler_resources=None,
    worker_env=None,
    scheduler_env=None,
    worker_command="dask-worker",
    scheduler_service_type="ClusterIP",
    idle_timeout=0,
    jupyter=False,
):
    return {
        "apiVersion": "kubernetes.dask.org/v1",
        "kind": "DaskCluster",
        "metadata": {"name": name},
        "spec": {
            "idleTimeout": idle_timeout,
            "worker": make_worker_spec(
                env=worker_env,
                resources=worker_resources,
                worker_command=worker_command,
                n_workers=n_workers,
                image=image,
            ),
            "scheduler": make_scheduler_spec(
                cluster_name=name,
                env=scheduler_env,
                resources=scheduler_resources,
                image=image,
                scheduler_service_type=scheduler_service_type,
                jupyter=jupyter,
            ),
        },
    }

from dask.distributed import PipInstall
from dask_kubernetes.operator import KubeCluster

worker_resources = {"requests": {"memory": "1Gi", "cpu": "1"}, "limits": {"memory": "2Gi", "cpu": "2"}}
scheduler_resources = {"requests": {"memory": "2Gi", "cpu": "1"}, "limits": {"memory": "3Gi", "cpu": "2"}}
worker_env = {"Worker": "TEST"}
scheduler_env = {"Scheduler": "TEST"}
# worker_env.update({"EXTRA_PIP_PACKAGES": "s3fs"})
# scheduler_env.update({"EXTRA_PIP_PACKAGES": "prometheus_client"})
spec = dask_make_cluster_spec(name="my-dask-cluster",
                              image='ghcr.io/dask/dask:2024.5.2-py3.11',
                              n_workers=0,
                              worker_env=worker_env,
                              scheduler_env=scheduler_env,
                              worker_resources=worker_resources,
                              scheduler_resources=scheduler_resources)
# spec["spec"]["worker"]["spec"]["nodeSelector"] = {"my_node": "true"}
# spec["spec"]["scheduler"]["spec"]["nodeSelector"] = {"my_node": "true"}

cluster = KubeCluster(custom_cluster_spec=spec)
cluster.adapt(minimum=1, maximum=2)

from dask.distributed import Client

client = Client(cluster)
plugin = PipInstall(packages=["s3fs==2024.3.1"], pip_options=["--upgrade"])
client.register_plugin(plugin)