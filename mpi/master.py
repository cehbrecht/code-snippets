import sys
from mpi4py import MPI


if __name__ == '__main__':
    comm = MPI.COMM_SELF.Spawn(
        sys.executable,
        args=['sleep.py'],
        maxprocs=5)
    comm.Disconnect()
