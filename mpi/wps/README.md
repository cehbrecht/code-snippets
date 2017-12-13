# Python MPI examples

## Create Conda environment and install mpi4py

```
$ conda env create -f environment.yml
$ source activate pywps-mpi
$ conda remove mpi4py mpich mpich2 --force
$ pip install mpi4py --no-deps
$ export MPI4PY_MAX_WORKERS=1 # or more if you have enough CPUs
```

When pip installation of `mpi4py` fails it might help to install the openmpi headers:

```
$ sudo apt-get install libopenmpi-dev
``` 

## Sleep WPS process with MPI

```
$ pytest wps_sleep.py
$ less sleep.log
```

## WPS process to calculate mean with OCGIS and MPI

```
$ pytest wps_mean.py
$ less mean.log
```
