# Python MPI examples

## Create Conda environment and install mpi4py

```
$ conda env create -f environment.yml
$ source activate pywps-mpi
$ pip install mpi4py --no-deps
```

## Quick hack to use MPI in a PyWPS process

```
$ pytest wps_sleep.py
$ less sleep.log
```
