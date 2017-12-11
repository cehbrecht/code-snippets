from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata


import os
import time
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import ocgis

from pywps.tests import WpsClient, WpsTestResponse
from pywps import Service
from pywps.tests import assert_response_success

import logging
LOGGER = logging.getLogger("PYWPS")

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))


def calc_with_ocgis(value=1):
    tic = time.time()

    dist = ocgis.vmachine.mpi.OcgDist()
    dim = dist.create_dimension('foo', 10, dist=True)
    dist.update_dimension_bounds()

    var = ocgis.Variable(name='a_var', dimensions=dim)
    var.get_value()[:] = value

    output = os.path.join(MODULE_PATH, 'output.nc')
    var.parent.write(output)

    # notify about completion
    tac = time.time()
    msg = "Completion time [#{}/{}]: {} seconds\n".format(ocgis.vm.rank, ocgis.vm.size, tac - tic)
    print(msg)
    with open(os.path.join(MODULE_PATH, 'calc.log'), 'a') as fp:
        fp.write(msg)
        if ocgis.vm.rank == 0:
            invar = ocgis.RequestDataset(output).get_field()['a_var']
            fp.write('Value on disk: {}\n'.format(invar.get_value()))
    return "done"


class Calculate(Process):
    def __init__(self):
        inputs = [
            LiteralInput('number', 'Just a Number',
                         default='1', data_type='integer')
        ]
        outputs = [
            LiteralOutput('output', 'Output', data_type='string')
        ]

        super(Calculate, self).__init__(
            self._handler,
            identifier='calc',
            version='1.0',
            title='Calculator',
            abstract='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        number = request.inputs['number'][0].data
        response.update_status('PyWPS Process started. Waiting...', 50)
        with MPIPoolExecutor(max_workers=None, path=[MODULE_PATH]) as executor:
            data = [number for i in range(4)]
            result = executor.map(calc_with_ocgis, data)
            for value in result:
                print value
            response.outputs['output'].data = 'done'
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
    client = client_for(Service(processes=[Calculate()], cfgfiles=['pywps.cfg']))
    datainputs = "number=1"
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0', identifier='calc',
        datainputs=datainputs)
    print(resp.response)
    assert_response_success(resp)
