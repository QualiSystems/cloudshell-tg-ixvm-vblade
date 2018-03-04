from cloudshell.cli.command_mode import CommandMode


class DefaultCommandMode(CommandMode):
    PROMPT = r'#'
    ENTER_COMMAND = ''
    EXIT_COMMAND = '\x03'  # Ctrl-C code  # todo: verify Ctrl-C action

    def __init__(self):
        super(DefaultCommandMode, self).__init__(DefaultCommandMode.PROMPT,
                                                 DefaultCommandMode.ENTER_COMMAND,
                                                 DefaultCommandMode.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {}
}
