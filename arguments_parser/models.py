class ArgFlag():
    """Information about one possible command line argument.
    """
    def __init__(self, main_flag: str, secondary_flag: str, variable_name: str, has_arguments: bool, argument_type: str | None, secondary_argument_type: str | None, help_message: str | None) -> None:
        self.main_flag = main_flag
        self.secondary_flag = secondary_flag
        self.variable_name = variable_name
        self.has_arguments = has_arguments
        self.argument_type = argument_type
        self.secondary_argument_type = secondary_argument_type
        self.help_message = help_message


class ArgFlagResponse():
    """Response, which contains the names of all command line arguments and their values in their needed format.
    """
    def __init__(self) -> None:
        """Create new object. Don't define any new variables while creating, set it as attributes later in code.
        """
        pass
