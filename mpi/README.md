# Python MPI examples

## Create Conda environment

```
$ conda env create
```

## Run sleep with mpi

```
$ mpiexec -n 2 python sleep.py
```

## Spawn sleep process using a master

```
$ mpiexec -n 1 python master.py
```

## Links

* https://mpi4py.scipy.org/docs/usrman/tutorial.html
