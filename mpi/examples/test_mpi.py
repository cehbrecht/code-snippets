#!/usr/bin/env python

import pytest
import mpi4py

from flyingpigeon.log import init_process_logger
from flyingpigeon.utils import archiveextract
from flyingpigeon.utils import rename_complexinputs


from pywps import Process
from pywps import ComplexInput, ComplexOutput
from pywps import Format
from pywps import Service
from pywps.tests import assert_response_success

from pywps.app.Common import Metadata

import time


from flyingpigeon.tests.common import TESTDATA, client_for, CFG_FILE

import ocgis
ocgis.env.OVERWRITE = True
#assert ocgis.vm.size_global == 2 # Assumes test run with mpirun -n 2 ./test_mpi.py

def run():
    tic = time.time()
    rd = ocgis.RequestDataset(TESTDATA['cmip5_tasmax_2006_nc'][6:])
    ops = ocgis.OcgOperations(dataset=rd, calc=[{'func': 'mean', 'name': 'mean'}], calc_grouping=['month'],)
    ops.execute()
    tac = time.time()
    print ("Completion time [#{}]: {} seconds".format(ocgis.vm.rank, tac-tic))

import logging
LOGGER = logging.getLogger("PYWPS")

class M1Process(Process):
    def __init__(self):
        inputs = [
            ComplexInput('resource', 'netCDF dataset',
                         abstract="Dissimilarity between target at selected "
                                   "location and candidate distributions over the entire grid.",
                         metadata=[Metadata('Info')],
                         min_occurs=1,
                         max_occurs=1,
                         supported_formats=[
                             Format('application/x-netcdf'),
                             Format('application/x-tar'),
                             Format('application/zip')]),]

        outputs = [

            ComplexOutput('output_netcdf', 'Dissimilarity values',
                          abstract="Dissimilarity between target at selected "
                                   "location and candidate distributions over the entire grid.",
                          as_reference=True,
                          supported_formats=[Format('application/x-netcdf')]
                          ),

            ComplexOutput('output_log', 'Logging information',
                          abstract="Collected logs during process run.",
                          as_reference=True,
                          supported_formats=[Format('text/plain')]
                          ),
        ]


        super(M1Process, self).__init__(
            self._handler,
            identifier="mpimean",
            title="Bla",
            abstract="Bla",
            version="0.1",
            metadata=[
                Metadata('Doc',
                         'http://flyingpigeon.readthedocs.io/en/latest/'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        resource = archiveextract(resource=rename_complexinputs(
            request.inputs['resource']))[0]

        init_process_logger('log.txt')
        response.outputs['output_log'].file = 'log.txt'

        LOGGER.info('Start process')
        LOGGER.debug("Rank : {}".format(ocgis.vm.rank))
        print("Rank : {}".format(ocgis.vm.rank))

        rd = ocgis.RequestDataset(resource)
        ops = ocgis.OcgOperations(dataset=rd,
                                  calc=[{'func': 'mean', 'name': 'mean'}],
                                  calc_grouping=['month'],
                                  output_format='nc')
        output = ops.execute()

        response.outputs['output_netcdf'].file = output

        response.update_status('Execution completed', 100)
        return response


def run_service():
    with ocgis.vm.scoped('Service launch', [0]):
        # There will be null communicators for the duration of the context manager.
        if not ocgis.vm.is_null:
            client = client_for(
                Service(processes=[M1Process()], cfgfiles=CFG_FILE))

            datainputs = "resource=files@xlink:href={0}".format(TESTDATA['cmip5_tasmax_2006_nc'])

            resp = client.get(
                service='wps', request='execute', version='1.0.0',
                identifier='mpimean',
                datainputs=datainputs)

            print(resp.response)

#run_service()
run()

