import time
import random
from mpi4py import MPI


def sleep():
    print("lets get some sleep ...")
    # mpi
    comm = MPI.COMM_WORLD
    # process start number 0, 1, ...
    rank = comm.Get_rank()
    # max number of processes
    size = comm.Get_size()
    # sleep code
    tic = time.time()
    time.sleep(random.randint(1, 3))
    tac = time.time()
    print("Completion time [#{}/{}]: {} seconds".format(rank, size, tac - tic))


if __name__ == '__main__':
    sleep()
