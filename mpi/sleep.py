import time
from mpi4py import MPI


def run():
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


if __name__ == '__main__':
    run()
