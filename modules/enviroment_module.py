import os, socket, psutil, requests
from typing import Dict, Any, List, Tuple
from core.interfaces import DiagnosticModule


class EnvironmentModule(DiagnosticModule):
    def __init__(self, name: str, mod_cfg: Dict[str, Any]):
        super().__init__(name)
        self._required_processes: List[str] = mod_cfg.get("required_processes") or []
        self._required_ports: List[int] = mod_cfg.get("required_ports") or []
        self._env_variables: List[str] = mod_cfg.get("env_variables") or []
        self._flow_settings_url: str = mod_cfg.get("_flow_settings_url") or ""

    @staticmethod
    def _is_port_open(port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)

                return s.connect_ex(("127.0.0.1", port)) == 0

        except Exception:
            return False

    @staticmethod
    def _get_running_processes() -> List[str]:
        running = []

        for proc in psutil.process_iter(attrs=["name"]):
            try:
                name = proc.info.get("name")
                if name:
                    running.append(name.lower())

            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                continue

        return running


    def _check_processes(self) -> Tuple[Dict[str, bool], bool]:
        processes_report = {}
        has_errors = False
        running_names = self._get_running_processes()

        for proc_name in self._required_processes:
            target = proc_name.lower()
            is_running = any(target in run_proc for run_proc in running_names)
            processes_report[proc_name] = is_running
            if not is_running:
                has_errors = True

        return processes_report, has_errors

    def _check_ports(self) -> Tuple[Dict[str, bool], bool]:
        ports_report = {}
        has_errors = False

        for port in self._required_ports:
            open_status = self._is_port_open(port)
            ports_report[str(port)] = open_status
            if not open_status:
                has_errors = True

        return ports_report, has_errors

    def _check_env_variables(self) -> Tuple[Dict[str, bool], bool]:
        env_report = {}
        has_errors = False

        for var in self._env_variables:
            exists = var in os.environ
            env_report[var] = exists
            if not exists:
                has_errors = True

        return env_report, has_errors

    def _sync_with_flow_settings(self) -> None:
        if not self._flow_settings_url:
            print(f"[INFO][{self.name}] URL для flow-settings не задан, синхронизация пропущена.")
            return

        try:
            print(f"[INFO][{self.name}] Синхронизация с flow-settings по адресу: {self._flow_settings_url}")

            response = requests.get(self._flow_settings_url, timeout=3.0)

            if response.status_code == 200:
                data = response.json()

                if "required_processes" in data:
                    self._required_processes = data["required_processes"]

                if "required_ports" in data:
                    self._required_ports = data["required_ports"]

                if "env_variables" in data:
                    self._env_variables = data["env_variables"]

                print(f"[INFO][{self.name}] Синхронизация успешна. Обновлено процессов: {len(self._required_processes)}")
            else:
                print(f"[WARNING][{self.name}] Сервис flow-settings вернул статус {response.status_code}")

        except Exception as e:
            print(
                f"[ERROR][{self.name}] Не удалось синхронизироваться с flow-settings: {e}. Используются локальные настройки.")


    def execute(self) -> Dict[str, Any]:
        self._sync_with_flow_settings()

        if not self._required_processes and not self._required_ports and not self._env_variables:
            return {
                "status": "WARNING",
                "processes_monitoring": {},
                "ports_monitoring": {},
                "env_variables": {}
            }

        procs_report, proc_errors = self._check_processes()
        ports_report, port_errors = self._check_ports()
        env_report, env_errors = self._check_env_variables()

        any_errors = proc_errors or port_errors or env_errors

        return {
            "status": "WARNING" if any_errors else "SUCCESS",
            "processes_monitoring": procs_report,
            "ports_monitoring": ports_report,
            "env_variables": env_report
        }