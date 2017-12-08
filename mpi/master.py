import sys
from mpi4py import MPI


if __name__ == '__main__':
    from mpi4py import MPI
    comm = MPI.COMM_WORLD.Spawn(
        sys.executable,
        args=["worker.py"],
        maxprocs=2)
    # comm.Barrier()
    comm.Disconnect()
