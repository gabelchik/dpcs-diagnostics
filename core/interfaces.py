from typing import Any, Dict
from abc import ABC, abstractmethod

class DiagnosticModule(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        raise NotImplementedError("Каждый модуль обязан реализовать метод execute()")


class ReportResponder(ABC):
    @abstractmethod
    def send_report(self, report: Dict[str, Any]) -> None:
        raise NotImplementedError("Каждый респондер обязан реализовать метод send_report()")
