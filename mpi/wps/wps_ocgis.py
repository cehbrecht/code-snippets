from pywps import Process, LiteralInput, LiteralOutput
from pywps import ComplexInput, ComplexOutput
from pywps.app.Common import Metadata
from pywps.tests import WpsClient, WpsTestResponse
from pywps import Service
from pywps import Format
from pywps.tests import assert_response_success


import os
import time
from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import ocgis
ocgis.env.OVERWRITE = True


import logging
LOGGER = logging.getLogger("PYWPS")

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))


def calc(value):
    tic = time.time()
    rd = ocgis.RequestDataset(
        os.path.join(MODULE_PATH, 'testdata', 'tasmax_Amon_MPI-ESM-MR_rcp45_r1i1p1_200601-200612.nc'))
    ops = ocgis.OcgOperations(
        dataset=rd,
        calc=[{'func': 'mean', 'name': 'mean'}],
        calc_grouping=['month'],
        output_format='nc')
    output = ops.execute()
    # notify about completion
    tac = time.time()
    msg = "Completion time [#{}/{}]: {} seconds\n".format(ocgis.vm.rank, ocgis.vm.size, tac - tic)
    print(msg)
    with open(os.path.join(MODULE_PATH, 'calc.log'), 'a') as fp:
        fp.write(msg)
        if ocgis.vm.rank == 0:
            tasmax = ocgis.RequestDataset(output).get_field()['mean']
            fp.write('Value on disk: {}\n'.format(tasmax.get_value()[:1]))
    return output


class Calculate(Process):
    def __init__(self):
        inputs = [
            LiteralInput('number', 'Just a Number',
                         default='1', data_type='integer')
        ]
        outputs = [
            ComplexOutput('output', 'Output',
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]
                          ),
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
            result = executor.map(calc, data)
            for value in result:
                print value
            response.outputs['output'].file = value
            # raise Exception(value)
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
