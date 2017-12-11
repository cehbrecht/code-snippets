import time
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor


def sleep(seconds, name, mymap):
    print("lets get some sleep ...")
    print('seconds: {}, name: {}', seconds, name)
    print(mymap)
    # mpi
    comm = MPI.COMM_WORLD
    # process start number 0, 1, ...
    rank = comm.Get_rank()
    # max number of processes
    size = comm.Get_size()
    # sleep code
    tic = time.time()
    time.sleep(seconds)
    tac = time.time()
    print("Completion time [#{}/{}]: {} seconds".format(rank, size, tac - tic))
    return mymap


if __name__ == '__main__':
    # with MPIPoolExecutor(max_workers=4) as executor:
    with MPIPoolExecutor() as executor:
        future = executor.submit(sleep, seconds=1, name='sleep', mymap={'one': 1, 'two': 2})
        print(future.result())
