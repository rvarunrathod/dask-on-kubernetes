from dask_kubernetes.operator import KubeCluster

cluster = KubeCluster(name="my-dask-cluster", image='ghcr.io/dask/dask:2024.5.2-py3.11')
cluster.scale(n=2)

from dask.distributed import Client
client = Client(cluster)

import dask
df = dask.datasets.timeseries() #generate random data
len(df.index) #length of dataframe
df.head(5)

aggregated_X = df.groupby('name').x.sum() #group by name and sum x column value
output = client.compute(aggregated_X) #submit this task to worker
output.result() #gather result

client.close() #close the connection to cluster
cluster.close() #delete the cluster