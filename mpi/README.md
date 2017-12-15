# Python MPI examples

* `basics/`: basic examples
* `wps/`: MPI example with PyWPS

## OCGIS example

Very simple mean calculation script that will execute in parallel:

https://github.com/NCPP/ocgis/blob/master/examples/simple_mean.py

Some things should be done on rank 0 like deleting files, prints, etc.
Otherwise, there is nothing special. 
It is worth noting that the environment variable `ocgis.env.ADD_OPS_MPI_BARRIER`
controls the use of an MPI barrier at the end of `OcgOperations`.
The default is `True`.
Setting this to `False` may be useful for debugging as tracebacks
 are more likely to appear versus a hanging operation.
 This is `True` by default to help avoid race conditions...

## Using MPI Spawn

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
