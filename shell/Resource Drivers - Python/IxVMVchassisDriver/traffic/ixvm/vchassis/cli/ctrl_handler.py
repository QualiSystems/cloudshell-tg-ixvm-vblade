from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.devices.cli_handler_impl import CliHandlerImpl

from traffic.ixvm.vchassis.cli.ctrl_command_modes import DefaultCommandMode


class IxVMControllerCliHandler(CliHandlerImpl):
    def __init__(self, cli, resource_config, logger, api):
        """

        :param cloudshell.cli.cli.CLI cli: CLI object
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession api: cloudshell API object
        """
        super(IxVMControllerCliHandler, self).__init__(cli, resource_config, logger, api)
        self._modes = CommandModeHelper.create_command_mode()

    @property
    def default_mode(self):
        return self._modes[DefaultCommandMode]

    @property
    def cli_mode(self):
        return self.default_mode

    @property
    def enable_mode(self):
        return self.default_mode

    @property
    def config_mode(self):
        return self.default_mode
