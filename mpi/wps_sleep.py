from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata

import os
import json
import dill
# import pickle


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
        # job = dict(uuid=response.uuid.hex)
        # job['request'] = json.loads(request.json)
        with open('request.json', 'w') as fp:
            fp.write(request.json)
        with open('response.dump', 'w') as fp:
            dill.dump(response, fp)
            # pickle.dump(response, fp)
        return mpi_launcher()

# the processing function


def sleep(request, response):
    import time

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
    client = client_for(Service(processes=[Sleep()]))
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
    return response


if __name__ == '__main__':
    mpi_launcher()
