from cloudshell.devices.standards.traffic.virtual.autoload_structure import Chassis
from cloudshell.devices.standards.traffic.virtual.autoload_structure import Module
from cloudshell.devices.standards.traffic.virtual.autoload_structure import Port


class IxVMChassis(Chassis):
    RESOURCE_MODEL = "IxVM Virtual Chassis"


class IxVMModule(Module):
    pass


class IxVMPort(Port):
    pass
