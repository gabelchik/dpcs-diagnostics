import psutil
from typing import Dict, Any
from core.interfaces import DiagnosticModule


class ResourceModule(DiagnosticModule):
    def __init__(self, name: str, limits: Dict[str, float]):
        super().__init__(name)
        self.limits = limits

    def execute(self) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=5)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        is_critical = (
                cpu > self.limits.get("cpu_percent", 100) or
                ram > self.limits.get("ram_percent", 100) or
                disk > self.limits.get("disk_percent", 100)
        )

        return {
            "module": self.name,
            "status": "CRITICAL" if is_critical else "OK",
            "metrics": {
                "cpu_percent": cpu,
                "ram_percent": ram,
                "disk_percent": disk
            }
        }