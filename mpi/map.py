import time
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor


def sleep(input):
    print("lets get some sleep ...")
    print(input)
    # mpi
    comm = MPI.COMM_WORLD
    # process start number 0, 1, ...
    rank = comm.Get_rank()
    # max number of processes
    size = comm.Get_size()
    # sleep code
    tic = time.time()
    time.sleep(1)
    tac = time.time()
    print("Completion time [#{}/{}]: {} seconds".format(rank, size, tac - tic))
    return str(input)


if __name__ == '__main__':
    with MPIPoolExecutor() as executor:
        result = executor.map(sleep, range(4))
        for value in result:
            print(value)
