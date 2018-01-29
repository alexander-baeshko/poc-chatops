#!/usr/bin/env python

import pepper
from errbot import BotPlugin, botcmd, ShlexArgParser
from errbot.templating import tenv


class SaltApiRequest(object):
    """
    Request helper
    """
    _api_endpoint = None
    _bot_config = None

    def __init__(self, bot_config):
        self._bot_config = bot_config

    def _connect(self):
        try:
            username = self._bot_config.SALT_API_USERNAME
            password = self._bot_config.SALT_API_PASSWORD
            eauth = self._bot_config.SALT_API_EAUTH
            url = self._bot_config.SALT_API_URL
            if self._api_endpoint is None:
                self._api_endpoint = pepper.Pepper(url, debug_http=False)
                self._api_endpoint.login(username=username,
                                         password=password,
                                         eauth=eauth)
            return self._api_endpoint
        except:
            raise Exception("Could no establish connection with Salt API")

    def _validate_arguments(self, args):
        if not isinstance(args, list) or len(args) != 2:
            raise Exception("Arguments validation failed")


class MinionsRequest(SaltApiRequest):
    """
    /minions request
    """
    def request(self):
        api = self._connect()
        response = api.req_get('/minions')
        return response


class GlobRequest(SaltApiRequest):
    """
    /glob request
    """
    def request(self, args):
        self._validate_arguments(args)
        targets = args[0]
        command = args[1]
        api = self._connect()
        response = api.local(targets, 'cmd.run', arg=command,
                             kwarg=None, expr_form='glob')
        return response


class GrainRequest(SaltApiRequest):
    """
    /grain request
    """
    def request(self, args):
        self._validate_arguments(args)
        targets = args[0]
        command = args[1]
        api = self._connect()
        response = api.local(targets,
                             'cmd.run',
                             arg=command,
                             kwarg=None,
                             expr_form='grain')
        return response


class SaltApiResponse(object):
    """
    Response helper
    """
    _input = None
    _input_valid = False

    def __init__(self, response):
        self._input = response
        self._validate_input(response)
        if self._input is None or self._input_valid is not True:
            raise Exception("Response validation failed")

    def _validate_input(self, response):
        if 'return' in response.keys():
            if response['return'] and isinstance(response['return'], list):
                if isinstance(response['return'][0], dict) and response['return'][0].keys():
                    self._input_valid = True


class MinionsResponse(SaltApiResponse):
    """
    /minions response
    """
    def response(self):
        minions = self._input['return'][0].keys()
        response = tenv().get_template('minions.j2').render(minions=minions)
        return response


class GlobResponse(SaltApiResponse):
    """
    /glob response
    """
    def response(self, args):
        minions = self._input['return'][0].keys()
        data = self._input['return'][0]
        command = args[1]
        response = tenv().get_template('glob.j2').render(minions=minions,
                                                         data=data,
                                                         command=command)
        return response


class GrainResponse(SaltApiResponse):
    """
    /grain
    """
    def response(self, args):
        minions = self._input['return'][0].keys()
        data = self._input['return'][0]
        command = args[1]
        response = tenv().get_template('grain.j2').render(minions=minions,
                                                          data=data,
                                                          command=command)
        return response


class SaltTelegram(BotPlugin):  # pylint: disable=too-many-ancestors
    """
    Basic Telegram bot for remote shell commands execution using SaltStack
    """
    @botcmd
    def minions(self, msg, args):
        """
        Returns list of avaliable saltmaster minions
        """
        configuration = self.bot_config
        api_response = MinionsRequest(configuration).request()
        client_response = MinionsResponse(api_response).response()
        self.send(msg.frm, client_response)

    @botcmd(split_args_with=ShlexArgParser())
    def glob(self, msg, args):
        """
        Executes command using glob target and returns its output
        """
        configuration = self.bot_config
        api_response = GlobRequest(configuration).request(args)
        client_response = GlobResponse(api_response).response(args)
        self.send(msg.frm, client_response)

    @botcmd(split_args_with=ShlexArgParser())
    def grain(self, msg, args):
        """
        Executes command using grain target and returns its output
        """
        configuration = self.bot_config
        api_response = GrainRequest(configuration).request(args)
        client_response = GrainResponse(api_response).response(args)
        self.send(msg.frm, client_response)
