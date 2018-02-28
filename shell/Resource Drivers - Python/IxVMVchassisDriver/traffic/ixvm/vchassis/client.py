import httplib

import requests


class IxVMChassisHTTPClient(object):
    def __init__(self, address, user=None, password=None, scheme="https", port=443, verify_ssl=False):
        """
        :param str address: controller IP address
        :param str user: controller username
        :param str password: controller password
        :param str scheme: protocol (http|https)
        :param int port: controller port
        :param bool verify_ssl: whether SSL cert will be verified or not
        """
        self._base_url = "{}://{}:{}".format(scheme, address, port)
        self._headers = {"Content-Type": "application/json"}
        self._user = user
        self._password = password
        self._verify_ssl = verify_ssl

    def _do_get(self, path, raise_for_status=True, **kwargs):
        """Basic GET request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        kwargs.update({"verify": self._verify_ssl})
        resp = requests.get(url=url, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_post(self, path, raise_for_status=True, **kwargs):
        """Basic POST request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        kwargs.update({"verify": self._verify_ssl})
        resp = requests.post(url=url, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_put(self, path, raise_for_status=True, **kwargs):
        """Basic PUT request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        kwargs.update({"verify": self._verify_ssl})
        resp = requests.put(url=url, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def _do_delete(self, path, raise_for_status=True, **kwargs):
        """Basic DELETE request client method

        :param str path: path for the request
        :param dict kwargs: additional kwarg that would be passed to the requests lib
        :rtype: requests.Response
        """
        url = "{}/{}".format(self._base_url, path)
        kwargs.update({"verify": self._verify_ssl})
        resp = requests.delete(url=url, headers=self._headers, **kwargs)
        raise_for_status and resp.raise_for_status()
        return resp

    def login(self):
        """

        :return:
        """
        data = {
            "username": self._user,
            "password": self._password,
            "rememberMe": True
        }
        resp = self._do_post(path="platform/api/v1/auth/session", json=data)
        resp = resp.json()
        self._headers.update({"x-api-key": resp["apiKey"]})

    def get_chassis(self):
        """"""
        resp = self._do_get(path="chassis/api/v2/ixos/chassis")
        resp = resp.json()

        return resp

    def get_cards(self):
        """"""
        resp = self._do_get(path="chassis/api/v2/ixos/cards")
        resp = resp.json()

        return resp

    def get_ports(self):
        """"""
        resp = self._do_get(path="chassis/api/v2/ixos/ports")
        resp = resp.json()

        return resp

    def check_if_service_is_deployed(self, logger):
        """
        :return:
        """
        ""
        try:
            resp = self._do_get(path="platform", raise_for_status=False)
        except requests.exceptions.ConnectionError:
            return False

        return resp.status_code == httplib.OK

