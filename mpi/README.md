# Python MPI examples

* `basics/`: basic examples
* `wps/`: MPI example with PyWPS

## Troubleshooting

### Using MPI Spawn

With `mpich2` you need to run a MPI spawn with:

```
$ mpiexec -n 1 python master.py
```

If you want to use it without `mpiexec` you need the `openmpi` library:

```
$ python master.py
```

https://groups.google.com/forum/#!topic/mpi4py/9C6SY4ZY7LI

## Links

* https://pypi.python.org/pypi/mpi4py
* https://mpi4py.scipy.org/docs/usrman/tutorial.html
