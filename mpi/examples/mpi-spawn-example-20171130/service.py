import sys


def run():
    import ocgis

    print('Hello from run(). I am rank: {}'.format(ocgis.vm.rank))

    dist = ocgis.vmachine.mpi.OcgDist()
    dim = dist.create_dimension('foo', 10, dist=True)
    dist.update_dimension_bounds()

    var = ocgis.Variable(name='a_var', dimensions=dim)
    var.get_value()[:] = ocgis.vm.rank

    var.parent.write('a_var_data.nc')

    if ocgis.vm.rank == 0:
        invar = ocgis.RequestDataset('a_var_data.nc').create_field()['a_var']
        print('Value on disk:', invar.get_value())


def run_service():
    from mpi4py import MPI
    comm = MPI.COMM_WORLD.Spawn(sys.executable,
                                args=['run_service.py'],
                                maxprocs=2)
    comm.Disconnect()


if __name__ == '__main__':
    run_service()
