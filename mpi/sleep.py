import time
from mpi4py import MPI


def run():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    tic = time.time()
    time.sleep(1)
    tac = time.time()
    print("Completion time [#{}]: {} seconds".format(rank, tac - tic))


if __name__ == '__main__':
    run()
