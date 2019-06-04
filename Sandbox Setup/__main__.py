from cloudshell.workflow.orchestration.sandbox import Sandbox
from cloudshell.workflow.orchestration.setup.default_setup_orchestrator import DefaultSetupWorkflow
from cloudshell.workflow.orchestration.setup.ixia.setup_orchestrator import IxiaSetupWorkflow

sandbox = Sandbox()

DefaultSetupWorkflow().register(sandbox)
IxiaSetupWorkflow().register(sandbox)

sandbox.execute_setup()
