from typing import cast
from arguments_parser.models import ArgFlag, ArgFlagResponse


class ArgParse():
    """Command line arguments' parser.
    """
    possible_argument_type: list[str] = ["str", "int", "float", "list", "tuple", "bool"]
    possible_secondary_type: list[str] = ["str", "int", "float", "bool"]

    def __init__(self, output_class=None) -> None:
        """Create new command line arguments' parser.
        """
        self.arguments: list[ArgFlag] = []      # NOTE: Hold all the possible arguments
        # NOTE: Hold object, which contains all the parsed arguments and their values
        if not output_class:
            self.parsed_arguments: ArgFlagResponse = ArgFlagResponse()
        else:
            self.parsed_arguments = output_class

    def add_argument(self, main_flag: str, secondary_flag: str, variable_name: str, argument_type: str | None = None, secondary_argument_type: str | None = None, has_arguments: bool = True, help_message: str | None = None) -> None:
        """Add new possible command line argument.

        Parameters
        ----------
        main_flag : str
            One of the main possible flags to use. My favourite format: --[name]
        secondary_flag : str
            What other flag name can be used. It can be shortened version for it. My favourite format: -[n]
        variable_name : str
            The name that will be used, when the parsed arguments are given back
        argument_type : str, optional
            How to format the given arguments when returning created object, by default None. Possible values: str, int, float, list, tuple, bool. If passed as None, doesn't convert
        secondary_argument_type : str, optional
            If argument_type is 'list', we can define, what kind of variable should it's contents be, by default None. Possible values: str, int, float, bool. If passed as None, doesn't convert
        has_arguments : bool, optional
            Does it contain any arguments by default, or is it used as boolean, by default True
        help_message : str, optional
            When user wants some help, what message will be near this argument, by default None

        Raises
        ------
        TypeError
            If main_flag type is not str
        TypeError
            If secondary_flag type is not str
        TypeError
            If variable_name type is not str
        TypeError
            If argument_type is given and type is not str
        TypeError
            If secondary_argument_type is given and type is not str
        TypeError
            If has_arguments is given and it's type is not bool
        TypeError
            If help_message is given and it's type is not str
        ValueError
            If argument_type type is not str
        ValueError
            If help_message is given and it's type is not str
        """
        # NOTE: Check if variable types are all correct
        if not isinstance(main_flag, str):
            raise TypeError("main_flag must be of type str")
        if not isinstance(secondary_flag, str):
            raise TypeError("secondary_flag must be of type str")
        if not isinstance(variable_name, str):
            raise TypeError("variable_name must be of type str")
        if has_arguments and not isinstance(has_arguments, bool):
            raise TypeError("has_arguments must be of type bool")
        if argument_type and not isinstance(argument_type, str):
            raise TypeError("argument_type must be of type str")
        if secondary_argument_type and not isinstance(secondary_argument_type, str):
            raise TypeError("secondary_argument_type must be of type str")
        if help_message and not isinstance(help_message, str):
            raise TypeError("help_message must be of type str")

        # NOTE: Check if argument_type and secondary_argument_type are given correct values
        if argument_type and argument_type not in ArgParse.possible_argument_type:
            raise ValueError(f"argument_type must be equal to any of these values: str, int, float, list, tuple, bool. We got: {argument_type}")
        if secondary_argument_type and secondary_argument_type not in ArgParse.possible_secondary_type:
            raise ValueError(f"argument_type must be equal to any of these values: str, int, float, bool. We got: {argument_type}")

        self.arguments.append(ArgFlag(main_flag, secondary_flag, variable_name, has_arguments, argument_type, secondary_argument_type, help_message))

    def parse_arguments(self, arguments_list: list[str | int]) -> ArgFlagResponse:
        for i, argument in enumerate(arguments_list):
            # NOTE: Check if current value exists in a dict
            # NOTE: Check if it's string and starts with '-' (means flag name is here)
            if isinstance(argument, str) and argument[0] == "-":
                args: list[str | int] = []
                possible_arg_flags: list[ArgFlag] = [obj for obj in self.arguments if obj.main_flag == argument or obj.secondary_flag == argument]
                # NOTE: If the flag isn't found in our allowed flags list, we raise ValueError
                if not possible_arg_flags:
                    raise ValueError(f"{argument} was not found in allowed flags list")
                arg_flag: ArgFlag = possible_arg_flags[0]
                del possible_arg_flags
                if arg_flag.has_arguments:
                    for count in range(i + 1, len(arguments_list)):
                        # NOTE: If this item shows the beginning of flag, we break from the loop
                        if isinstance(arguments_list[count], str) and cast(str, arguments_list[count])[0] == "-":
                            break
                        args.append(arguments_list[count])   # NOTE: Currently just append all the arguments to current arg list
                    # NOTE: If we couldn't find any arguments, but this flag requires them, raise error
                    if not args:
                        raise ValueError(f"Shouldn't {argument} have any kind of flags?")
                else:
                    setattr(self.parsed_arguments, arg_flag.variable_name, True)
                # NOTE: Format current flag arguments based on the given requirement
                # NOTE: Find what is the wanted primary argument type and format accordingly
                # If the type is None, we skip (leave as is)
                if not arg_flag.argument_type:
                    continue
                if arg_flag.argument_type in ["str", "int", "float", "bool"]:
                    new_argument: str | int | float | bool | None = None
                    try:
                        match arg_flag.argument_type:
                            case "str":
                                new_argument = str(args[0])
                            case "int":
                                new_argument = int(args[0])
                            case "float":
                                new_argument = float(args[0])
                            case "bool":
                                new_argument = bool(args[0])
                            case _:
                                new_argument = args[0]
                    except ValueError:
                        raise ValueError(f"Converting types raised an error, converting variable: {args[0]}, converting to type: {arg_flag.argument_type}")
                    setattr(self.parsed_arguments, arg_flag.variable_name, new_argument)
                    del new_argument
                    continue

                if arg_flag.argument_type in ["list", "tuple"]:
                    new_arguments: list | tuple | None = None
                    try:
                        match arg_flag.argument_type:
                            case "list":
                                new_arguments = self._convert_iterable_content(args, cast(str, arg_flag.secondary_argument_type))
                            case "tuple":
                                new_arguments = tuple(self._convert_iterable_content(args, cast(str, arg_flag.secondary_argument_type)))
                    except ValueError:
                        raise ValueError(f"Converting types raised an error, converting variable: {args}, converting to type: {arg_flag.argument_type}")
                    setattr(self.parsed_arguments, arg_flag.variable_name, new_arguments)
                    del new_arguments
                    continue
        return self.parsed_arguments

    def _convert_iterable_content(self, arguments_list: list[str | int], convert_to: str) -> list[str | int | float | bool]:
        match convert_to:
            case "str":
                return [str(item) for item in arguments_list]
            case "int":
                return [int(item) for item in arguments_list]
            case "float":
                return [float(item) for item in arguments_list]
            case "bool":
                return [bool(item) for item in arguments_list]
            case _:
                return [item for item in arguments_list]
