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


import logging
LOGGER = logging.getLogger("PYWPS")

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))

WIDTH = 640 * 2
HEIGHT = 480 * 2

x0, x1 = -2.0, +2.0
y0, y1 = -1.5, +1.5

c = complex(0, 0.65)


def julia(x, y):
    z = complex(x, y)
    n = 255
    while abs(z) < 3 and n > 1:
        z = z**2 + c
        n -= 1
    return n


def julia_line(k):
    dx = (x1 - x0) / WIDTH
    dy = (y1 - y0) / HEIGHT
    line = bytearray(WIDTH)
    y = y1 - k * dy
    for j in range(WIDTH):
        x = x0 + j * dx
        line[j] = julia(x, y)
    return line


class Julia(Process):
    def __init__(self):
        inputs = [
            LiteralInput('width', 'Image Width',
                         default=640, data_type='integer'),
            LiteralInput('height', 'Image Height',
                         default=480, data_type='integer'),
        ]
        outputs = [
            ComplexOutput('output', 'Output',
                          as_reference=True,
                          supported_formats=[Format('image/x-portable-greymap')]
                          ),
        ]

        super(Julia, self).__init__(
            self._handler,
            identifier='julia',
            version='1.0',
            title='Julia Fractal Image',
            abstract='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        WIDTH = request.inputs['width'][0].data * 2
        HEIGHT = request.inputs['height'][0].data * 2
        response.update_status('Julia started. Waiting...', 10)
        tic = time.time()
        with MPIPoolExecutor(max_workers=None, timeout=10, path=[MODULE_PATH]) as executor:
            image = executor.map(julia_line, range(HEIGHT))
            with open('julia.pgm', 'wb') as f:
                f.write(b'P5 %d %d %d\n' % (WIDTH, HEIGHT, 255))
                for line in image:
                    f.write(line)
                response.outputs['output'].file = 'julia.pgm'
        tac = time.time()
        msg = "Completion time {} seconds\n".format(tac - tic)
        print(msg)
        with open(os.path.join(MODULE_PATH, 'julia.log'), 'a') as fp:
            fp.write(msg)
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
    client = client_for(Service(processes=[Julia()], cfgfiles=['pywps.cfg']))
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0', identifier='julia',
        datainputs="width=640;height=480;")
    print(resp.response)
    assert_response_success(resp)
