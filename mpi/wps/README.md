# Python MPI examples

## Create Conda environment and install mpi4py

```
$ conda env create -f environment.yml
$ source activate pywps-mpi
$ conda remove mpi4py mpich --force
$ pip install mpi4py --no-deps
```

## Sleep WPS process with MPI

```
$ pytest wps_sleep.py
$ less sleep.log
```

## OCGIS WPS process with MPI

```
$ pytest wps_ocgis.py
$ less calc.log
```
