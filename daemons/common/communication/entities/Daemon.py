from os import environ


class Daemon:
    instance = None
    default_name = environ.get("hostname", "daemon")

    def __init__(self) -> None:
        self.instance = self
        self.name = self.default_name

    def __new__(cls):
        if not cls.instance:
            return super().__new__(cls)
        return cls.instance
