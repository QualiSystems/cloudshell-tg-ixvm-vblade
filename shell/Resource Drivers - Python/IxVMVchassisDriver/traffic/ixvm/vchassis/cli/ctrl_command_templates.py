from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate


DEFAULT_ERROR_MAP = OrderedDict((("error:", "Error happens while executing CLI command"),))


def prepare_error_map(error_map=None):
    """

    :param collections.OrderedDict error_map:
    :rtype: collections.OrderedDict
    """
    if error_map is None:
        error_map = OrderedDict()

    error_map.update(DEFAULT_ERROR_MAP)
    return error_map


CONFIGURE_LICENSE_SERVER = CommandTemplate("set license-server {license_server_ip}", error_map=prepare_error_map())

RESTART_IXVM_SERVICE = CommandTemplate("restart-service ixServer", error_map=prepare_error_map())
