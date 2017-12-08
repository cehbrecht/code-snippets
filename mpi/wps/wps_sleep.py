from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata

import sys
import os
import json
import dill
import subprocess
from mpi4py import MPI

import logging
LOGGER = logging.getLogger("PYWPS")

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))


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
        with open('request.json', 'w') as fp:
            fp.write(request.json)
        with open('response.dump', 'w') as fp:
            dill.dump(response, fp)
        # mpi_launcher()
        # raise Exception("current dir=%s" % os.path.abspath(os.path.curdir))
        # raise Exception("which mpiexec=%s" % sys.executable)
        try:
            bin_dir = os.path.dirname(sys.executable)
            subprocess.check_output(
                [os.path.join(bin_dir, 'mpiexec'), '-n', '1',
                 sys.executable, os.path.join(MODULE_PATH, 'wps_sleep.py')],
                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            LOGGER.exception("mpi failed")
            raise
        with open('response.dump', 'r') as fp:
            response = dill.load(fp)
        return response

# the processing function


def sleep(request, response):
    import time

    tic = time.time()

    if 'delay' in request.inputs:
        sleep_delay = request.inputs['delay'][0].data
    else:
        sleep_delay = 10

    time.sleep(sleep_delay)
    response.update_status('PyWPS Process started. Waiting...', 50)
    print('zzzZ')
    time.sleep(sleep_delay)
    response.outputs['sleep_output'].data = 'done sleeping'
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

    return response

# unit test


from pywps.tests import WpsClient, WpsTestResponse
from pywps import Service
from pywps.tests import assert_response_success


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

# mpi launcher


def mpi_launcher():
    from pywps import WPSRequest
    request = WPSRequest()
    with open('request.json', 'r') as fp:
        request.json = json.load(fp)
    with open('response.dump', 'r') as fp:
        response = dill.load(fp)
    # do the job
    response = sleep(request, response)
    with open('response.dump', 'w') as fp:
        dill.dump(response, fp)


if __name__ == '__main__':
    mpi_launcher()
