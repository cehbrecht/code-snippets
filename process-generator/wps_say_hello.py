from pywps import Process, LiteralInput, LiteralOutput, UOM
from pywps.app.Common import Metadata

import logging
LOGGER = logging.getLogger("PYWPS")


class Welcome(Process):
    greeting = 'Hello'

    def __init__(self):
        inputs = [
            LiteralInput('name', 'Your name',
                         abstract='Please enter your name.',
                         data_type='string')]
        outputs = [
            LiteralOutput('output', 'Output response',
                          abstract='A friendly Hello from us.',
                          data_type='string')]

        super(Welcome, self).__init__(
            self._handler,
            identifier=self.greeting.lower(),
            title='Say Hello',
            abstract='Just says a friendly Hello.'
                     'Returns a literal string output with Hello plus the inputed name.',
            metadata=[
                Metadata('User Guide', 'https://emu.readthedocs.io/en/latest/processes.html'),  # noqa
                Metadata('PyWPS Demo', 'https://pywps-demo.readthedocs.io/en/latest/'),
            ],
            version='1.5',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        LOGGER.info("say hello")
        response.outputs['output'].data = self.greeting + ' ' + request.inputs['name'][0].data
        response.outputs['output'].uom = UOM('unity')
        return response

# process generator


def generate_welcome_clazz(cls_name, greeting):
    clazz = type(
        cls_name, (Welcome,), {'greeting': greeting})
    return clazz

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


def test_wps_welcome_to_hamburg():
    Hello = generate_welcome_clazz('WelcomeToHamburg', 'Moin')
    client = client_for(Service(processes=[Hello()], cfgfiles=['pywps.cfg']))
    datainputs = "name=Alice"
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0', identifier='moin',
        datainputs=datainputs)
    print(resp.response)
    assert_response_success(resp)


def test_wps_welcome_to_montreal():
    Hello = generate_welcome_clazz('WelcomeToMontreal', 'Bonjour')
    client = client_for(Service(processes=[Hello()], cfgfiles=['pywps.cfg']))
    datainputs = "name=WhiteRabbit"
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0', identifier='bonjour',
        datainputs=datainputs)
    print(resp.response)
    assert_response_success(resp)
