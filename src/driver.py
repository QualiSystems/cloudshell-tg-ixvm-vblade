import json
import time
from datetime import datetime
from datetime import timedelta

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.devices.autoload.autoload_builder import AutoloadDetailsBuilder
from cloudshell.devices.driver_helper import get_api
from cloudshell.devices.driver_helper import get_cli
from cloudshell.devices.driver_helper import get_logger_with_thread_id
from cloudshell.devices.standards.traffic.virtual.chassis.configuration_attributes_structure import TrafficGeneratorVChassisResource
from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.traffic.virtual.resource_driver_interface import VirtualTrafficGeneratorResourceDriverInterface
from cloudshell.traffic.virtual.runners.connect_child_resources import ConnectChildResourcesRunner

from traffic.ixvm.vchassis.api.client import IxVMChassisHTTPClient
from traffic.ixvm.vchassis.autoload import models
from traffic.ixvm.vchassis.runners.configuration_runner import IxVMConfigurationRunner


SERVICE_STARTING_TIMEOUT = 60 * 60
CHASSIS_STRUCTURE_APPEARANCE_TIMEOUT = 10 * 60
SHELL_TYPE = "CS_VirtualTrafficGeneratorChassis"
SHELL_NAME = "IxVM Virtual Traffic Chassis 2G"
MODULE_MODEL = "{}.VirtualTrafficGeneratorModule".format(SHELL_NAME)
PORT_MODEL = "{}.VirtualTrafficGeneratorPort".format(SHELL_NAME)


class IxVMVirtualChassisDriver(ResourceDriverInterface, VirtualTrafficGeneratorResourceDriverInterface):
    def __init__(self):
        """Constructor must be without arguments, it is created with reflection at run time"""
        self._cli = None

    def initialize(self, context):
        """Initialize the driver session, this function is called everytime a new instance of the driver is created.

        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        resource_config = TrafficGeneratorVChassisResource.from_context(context,
                                                                        shell_type=SHELL_TYPE,
                                                                        shell_name=SHELL_NAME)
        self._cli = get_cli(resource_config.sessions_concurrency_limit)
        return "Finished initializing"

    @staticmethod
    def _wait_for_service_deployment(api_client, logger):
        """

        :param api_client:
        :param logger:
        :return:
        """
        timeout_time = datetime.now() + timedelta(seconds=SERVICE_STARTING_TIMEOUT)

        while not api_client.check_if_service_is_deployed(logger):
            logger.info("Waiting for controller service start...")

            if datetime.now() > timeout_time:
                raise Exception("IxVM Chassis service didn't start within {} minute(s)"
                                .format(SERVICE_STARTING_TIMEOUT / 60))
            time.sleep(10)

    @staticmethod
    def _wait_for_chassis_structure(api_client, logger):
        """Will wait while chassis structure appears

        :param api_client:
        :param logger:
        :return:
        """
        timeout_time = datetime.now() + timedelta(seconds=CHASSIS_STRUCTURE_APPEARANCE_TIMEOUT)

        while not (api_client.get_cards() and api_client.get_ports()):
            logger.info("Waiting for chassis structure appearance...")

            if datetime.now() > timeout_time:
                raise Exception("Chassis data from IxVM Chassis service is empty and didn't appear within {}"
                                .format(CHASSIS_STRUCTURE_APPEARANCE_TIMEOUT / 60))
            time.sleep(10)

    def get_inventory(self, context):
        """Discovers the resource structure and attributes.

        :param AutoLoadCommandContext context: the context the command runs on
        :return Attribute and sub-resource information for the Shell resource you can return an AutoLoadDetails object
        :rtype: AutoLoadDetails
        """
        logger = get_logger_with_thread_id(context)
        logger.info("Autoload")

        with ErrorHandlingContext(logger):

            resource_config = TrafficGeneratorVChassisResource.from_context(context,
                                                                            shell_type=SHELL_TYPE,
                                                                            shell_name=SHELL_NAME)

            if not resource_config.address or resource_config.address.upper() == "NA":
                return AutoLoadDetails([], [])

            cs_api = get_api(context)
            password = cs_api.DecryptPassword(resource_config.password).Value

            logger.info("Initializing API client")

            api_client = IxVMChassisHTTPClient(address=resource_config.address,
                                               user=resource_config.user,
                                               password=password)

            logger.info("Waiting for API service to be deployed")
            self._wait_for_service_deployment(api_client, logger)

            configuration_operations = IxVMConfigurationRunner(resource_config=resource_config,
                                                               cli=self._cli,
                                                               cs_api=cs_api,
                                                               logger=logger)

            logger.info("Executing congfigure license server operation")
            configuration_operations.configure_license_server(license_server_ip=resource_config.license_server)

            logger.info("Performing API client login")
            api_client.login()

            logger.info("Waiting for the Chassis data")
            self._wait_for_chassis_structure(api_client, logger)

            logger.info("Retrieving Chassis data from the API")
            chassis_data = api_client.get_chassis()[0]
            chassis_id = chassis_data["id"]

            chassis_res = models.IxVMChassis(shell_type=SHELL_TYPE,
                                             shell_name=resource_config.shell_name,
                                             name="IxVm Virtual Chassis {}".format(chassis_id),
                                             unique_id=chassis_id)

            ports_data = {}
            for port_data in api_client.get_ports():
                parent_id = port_data["parentId"]
                port_number = port_data["portNumber"]

                ports_by_module = ports_data.setdefault(parent_id, [])
                ports_by_module.append(port_data)
                logger.info("Found Port {} under the parent id {}".format(port_number, parent_id))

            for module_data in api_client.get_cards():
                module_id = module_data["id"]
                module_number = module_data["cardNumber"]

                module_res = models.IxVMModule(shell_name=resource_config.shell_name,
                                               name="IxVm Virtual Module {}".format(module_number),
                                               unique_id=module_id)

                logger.info("Adding Module {} to the Chassis".format(module_number))
                chassis_res.add_sub_resource(module_number, module_res)

                for port_data in ports_data.get(module_id, []):
                    port_id = port_data["id"]
                    port_number = port_data["portNumber"]

                    port_res = models.IxVMPort(shell_name=resource_config.shell_name,
                                               name="Port {}".format(port_number),
                                               unique_id=port_id)

                    logger.info("Adding Port {} under the module {}".format(port_number, module_id))
                    module_res.add_sub_resource(port_number, port_res)

            return AutoloadDetailsBuilder(chassis_res).autoload_details()

    def cleanup(self):
        """ Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """

        pass

    def connect_child_resources(self, context):
        """
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info("Connect child resources command started")

        with ErrorHandlingContext(logger):
            resource_name = context.resource.fullname
            reservation_id = context.reservation.reservation_id
            connectors = context.connectors
            api = get_api(context)

            connect_operation = ConnectChildResourcesRunner(logger=logger,
                                                            cs_api=api)

            ports = connect_operation.get_ports(resource_name=resource_name,
                                                port_model=PORT_MODEL)

            return connect_operation.connect_child_resources(connectors=connectors,
                                                             ports=ports,
                                                             resource_name=resource_name,
                                                             reservation_id=reservation_id)

if __name__ == "__main__":
    import mock
    from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails

    address = '192.168.42.169'

    user = 'admin'
    password = 'admin'
    port = 443
    scheme = "https"
    auth_key = 'h8WRxvHoWkmH8rLQz+Z/pg=='
    api_port = 8029

    context = ResourceCommandContext()
    context.resource = ResourceContextDetails()
    context.resource.name = 'tvm_m_2_fec7-7c42'
    context.resource.fullname = 'tvm_m_2_fec7-7c42'
    context.reservation = ReservationContextDetails()
    context.reservation.reservation_id = '0cc17f8c-75ba-495f-aeb5-df5f0f9a0e97'
    context.resource.attributes = {}
    context.resource.attributes['{}.User'.format(IxVMVirtualChassisDriver.SHELL_NAME)] = user
    context.resource.attributes['{}.Password'.format(IxVMVirtualChassisDriver.SHELL_NAME)] = password
    context.resource.attributes['{}.License Server'.format(IxVMVirtualChassisDriver.SHELL_NAME)] = "192.168.42.61"
    context.resource.address = address
    context.resource.app_context = mock.MagicMock(app_request_json=json.dumps(
        {
            "deploymentService": {
                "cloudProviderName": "vcenter_333"
            }
        }))

    context.connectivity = mock.MagicMock()
    context.connectivity.server_address = "192.168.85.23"

    dr = IxVMVirtualChassisDriver()
    dr.initialize(context)

    with mock.patch('__main__.get_api') as get_api:
        get_api.return_value = type('api', (object,), {
            'DecryptPassword': lambda self, pw: type('Password', (object,), {'Value': pw})()})()

        result = dr.get_inventory(context)

        for res in result.resources:
            print res.__dict__
