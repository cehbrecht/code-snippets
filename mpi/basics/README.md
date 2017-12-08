# Basic Python MPI examples

## Create Conda environment and install mpi4py

```
$ conda env create -f environment.yml
$ source activate mpi
$ pip install mpi4py --no-deps
```

## Run sleep with mpi

```
$ mpiexec -n 2 python sleep.py
```

## Spawn sleep process using a master

```
$ mpiexec -n 1 python master.py
```

## ... and without `mpiexec` (openmpi only)

```
$ python master.py
```
