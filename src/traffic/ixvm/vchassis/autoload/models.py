from cloudshell.devices.standards.base import AbstractResource


AVAILABLE_SHELL_TYPES = ["CS_VirtualTrafficGeneratorChassis"]


class Chassis(AbstractResource):
    RESOURCE_MODEL = "IxVM Virtual Chassis"
    RELATIVE_PATH_TEMPLATE = "CH"

    def __init__(self, shell_name, name, unique_id, shell_type):
        super(Chassis, self).__init__(shell_name, name, unique_id)

        if shell_name:
            self.shell_name = "{}.".format(shell_name)
            if shell_type in AVAILABLE_SHELL_TYPES:
                self.shell_type = "{}.".format(shell_type)
            else:
                raise Exception(self.__class__.__name__, "Unavailable shell type {shell_type}."
                                                         "Shell type should be one of: {avail}"
                                .format(shell_type=shell_type, avail=", ".join(AVAILABLE_SHELL_TYPES)))
        else:
            self.shell_name = ""
            self.shell_type = ""


class Module(AbstractResource):
    RESOURCE_MODEL = "Virtual Traffic Generator Module"
    RELATIVE_PATH_TEMPLATE = "M"

    @property
    def device_model(self):
        """

        :return:
        """
        return self.attributes.get("{}Model".format(self.namespace), None)

    @device_model.setter
    def device_model(self, value):
        """

        :param value:
        :return:
        """
        self.attributes["{}Model".format(self.namespace)] = value


class Port(AbstractResource):
    RESOURCE_MODEL = "Virtual Traffic Generator Port"
    RELATIVE_PATH_TEMPLATE = "P"

    @property
    def logical_name(self):
        return self.attributes.get("{}Logical Name".format(self.namespace), None)

    @logical_name.setter
    def logical_name(self, value):
        """

        :param value:
        :return:
        """
        self.attributes["{}Logical Name".format(self.namespace)] = value

    @property
    def mac_address(self):
        """

        :return:
        """
        return self.attributes.get("{}MAC Address".format(self.namespace), None)

    @mac_address.setter
    def mac_address(self, value):
        """

        :param value:
        :return:
        """
        self.attributes["{}MAC Address".format(self.namespace)] = value
