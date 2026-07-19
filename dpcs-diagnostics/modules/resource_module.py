import psutil
from typing import Dict, Any
from core.interfaces import DiagnosticModule


class ResourceModule(DiagnosticModule):
    def __init__(self, name: str, mod_cfg: Dict[str, Any]):
        super().__init__(name)
        self._limits = mod_cfg.get("limits") or {}

    @staticmethod
    def _get_cpu_usage() -> float:
        return float(psutil.cpu_percent(interval=0.1))

    @staticmethod
    def _get_ram_usage() -> float:
        return float(psutil.virtual_memory().percent)

    @staticmethod
    def _get_disk_usage() -> float:
        return float(psutil.disk_usage('/').percent)


    def execute(self) -> Dict[str, Any]:
        cpu = self._get_cpu_usage()
        ram = self._get_ram_usage()
        disk = self._get_disk_usage()

        if not all(key in self._limits for key in ["max_cpu", "max_ram", "max_disk"]):
            return {
                "status": "FAILURE",
                "metrics": {
                    "cpu_percent": cpu,
                    "ram_percent": ram,
                    "disk_percent": disk
                },
                "limits": {}
            }

        is_failed = (
                cpu > self._limits.get("max_cpu") or
                ram > self._limits.get("max_ram") or
                disk > self._limits.get("max_disk")
        )

        return {
            "status": "FAILURE" if is_failed else "SUCCESS",
            "metrics": {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk
            },
            "limits": {
            "max_cpu": self._limits.get("max_cpu"),
            "max_ram": self._limits.get("max_ram"),
            "max_disk": self._limits.get("max_disk")
            }
        }