from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata


import os
import time
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor

from pywps.tests import WpsClient, WpsTestResponse
from pywps import Service
from pywps.tests import assert_response_success

import logging
LOGGER = logging.getLogger("PYWPS")

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))


def sleep(seconds=1):
    tic = time.time()

    print('zzzZ')
    time.sleep(seconds)
    print('... awake')

    # mpi
    comm = MPI.COMM_WORLD
    # process start number 0, 1, ...
    rank = comm.Get_rank()
    # max number of processes
    size = comm.Get_size()
    # notify about completion
    tac = time.time()
    msg = "Completion time [#{}/{}]: {} seconds\n".format(rank, size, tac - tic)
    print(msg)
    with open(os.path.join(MODULE_PATH, 'sleep.log'), 'a') as fp:
        fp.write(msg)
    # raise Exception("Akari!")
    return "sleeping done"


class Sleep(Process):
    def __init__(self):
        inputs = [
            LiteralInput('delay', 'Delay between every update',
                         default='10', data_type='float')
        ]
        outputs = [
            LiteralOutput('sleep_output', 'Sleep Output', data_type='string')
        ]

        super(Sleep, self).__init__(
            self._handler,
            identifier='sleep',
            version='1.0',
            title='Sleep Process',
            abstract='Testing a long running process, in the sleep.'
                     'This process will sleep for a given delay or 10 seconds if not a valid value.',
            profile='',
            metadata=[
                Metadata('User Guide', 'https://emu.readthedocs.io/en/latest/processes.html'),  # noqa
                Metadata('PyWPS Demo', 'https://pywps-demo.readthedocs.io/en/latest/'),
            ],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        if 'delay' in request.inputs:
            seconds = request.inputs['delay'][0].data
        else:
            seconds = 1
        response.update_status('PyWPS Process started. Waiting...', 50)
        with MPIPoolExecutor(max_workers=None, path=[MODULE_PATH]) as executor:
            # future = executor.submit(time.sleep, 1)
            future = executor.submit(sleep, seconds=seconds)
            print(future.result())
        response.outputs['sleep_output'].data = 'done sleeping'
        return response


# unit test

class WpsTestClient(WpsClient):

    def get(self, *args, **kwargs):
        query = "?"
        for key, value in kwargs.items():
            query += "{0}={1}&".format(key, value)
        return super(WpsTestClient, self).get(query)


def client_for(service):
    return WpsTestClient(service, WpsTestResponse)


def test_wps_sleep():
    client = client_for(Service(processes=[Sleep()], cfgfiles=['pywps.cfg']))
    datainputs = "delay=1.0"
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0', identifier='sleep',
        datainputs=datainputs)
    print(resp.response)
    assert_response_success(resp)
