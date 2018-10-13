"""
Pyairmore package
"""  # todo [1] package doc

__version__ = "0.1.0-pre"
__author__ = "Eray Erdin"


class Refreshable:
    # todo doc

    def refresh(self) -> None:
        raise NotImplementedError("This method needs to be overriden by children.")
