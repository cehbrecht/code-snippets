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

## Quick hack to use MPI in a PyWPS process

```
$ pytest wps_sleep.py
$ less sleep.log
```

## Troubleshooting

### Using MPI Spawn

https://groups.google.com/forum/#!topic/mpi4py/9C6SY4ZY7LI

## Links

* https://pypi.python.org/pypi/mpi4py
* https://mpi4py.scipy.org/docs/usrman/tutorial.html
