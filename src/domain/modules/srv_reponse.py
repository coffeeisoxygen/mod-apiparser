from domain.modules.sch_base import ResponseConfig, get_settings


class ResponseService:
    def __init__(self):
        self.settings = get_settings()

    def get_response_config_for_type(self, type_: str):
        """Retrieve the response configuration for a specific type.

        Args:
            type_ (str): The type of the response configuration to retrieve.

        Returns:
            The response configuration item if found, None otherwise.
        """
        for item in self.settings.responses.items:
            if item.type == type_:
                return item
        return None

    def get_global_response_config(self) -> ResponseConfig:
        """Retrieve the global response configuration.

        Returns:
            An instance of ResponseConfig containing the global settings.
        """
        return self.settings.response  # Return the full ResponseConfig object
