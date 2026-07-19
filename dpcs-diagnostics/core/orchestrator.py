import json, datetime
from typing import Dict, List, Any
from core.interfaces import DiagnosticModule, ReportResponder
from modules import MODULE_REGISTRY
from  responders import RESPONDER_REGISTRY


class DiagnosticCore:
    def __init__(self, config_path: str = "config.json"):
        self._config_path = config_path

        self._config: Dict[str, Any] = {}
        self._active_modules: List[DiagnosticModule] = []
        self._active_responders: List[ReportResponder] = []

        self.load_config()

    def load_config(self) -> None:
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            print(f"[INFO] Конфигурация успешно загружена из {self._config_path}")

        except Exception as e:
            print(f"[FATAL] Ошибка чтения конфигурационного файла {self._config_path}: {e}")
            self._config = {}

        modules_cfg = self._config.get("modules", {})
        for mod_key, mod_cfg in modules_cfg.items():
            if mod_cfg.get("active", False) and mod_key in MODULE_REGISTRY:
                klass = MODULE_REGISTRY[mod_key]
                try:
                    self._active_modules.append(klass(mod_key, mod_cfg))
                    print(f"[INFO] Модуль '{mod_key}' успешно зарегистрирован")

                except Exception as e:
                    print(f"[ERROR] Не удалось инициализировать модуль {mod_key}: {e}")

        responders_cfg = self._config.get("responders", {})
        for resp_key, resp_cfg in responders_cfg.items():
            if resp_cfg.get("active", False) and resp_key in RESPONDER_REGISTRY:
                klass = RESPONDER_REGISTRY[resp_key]

                init_kwargs = {k: v for k, v in resp_cfg.items() if k != "active"}

                try:
                    self._active_responders.append(klass(**init_kwargs))
                    print(f"[INFO] Респондер '{resp_key}' успешно зарегистрирован")
                except Exception as e:
                    print(f"[ERROR] Не удалось инициализировать респондер {resp_key}: {e}")

    def execute_diagnostics(self, target_modules: List[str] = None) -> dict:
        modules_to_run = self._active_modules

        if target_modules is not None:
            modules_to_run = [
                mod for mod in self._active_modules
                if mod.name in target_modules
            ]

        if not modules_to_run:
            print("[WARNING] Нет активных или подходящих модулей для запуска")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "node_name": self._config.get("node_name", "unknown_node"),
                "status": "WARNING",
                "modules": {},
                "message": "Диагностика не выявила модулей для запуска по указанным критериям"
            }

        print(f"[INFO] Запуск диагностики, всего модулей ({len(modules_to_run)})...")
        global_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "node_name": self._config.get("node_name", "unknown_node"),
            "status": "SUCCESS",
            "modules": {},
        }

        statuses_pool = []

        for module in modules_to_run:
            try:
                module_report = module.execute()
                global_report["modules"][module.name] = module_report
                statuses_pool.append(module_report.get("status"))

            except Exception as e:
                print(f"[ERROR] Ошибка при работе модуля {module.name}: {e}")
                global_report["modules"][module.name] = {
                    "status": "FAILURE",
                }
                statuses_pool.append("FAILURE")

        if "FAILURE" in statuses_pool:
            global_report["status"] = "FAILURE"
        elif "WARNING" in statuses_pool:
            global_report["status"] = "WARNING"
        else:
            global_report["status"] = "SUCCESS"

        print(f"[INFO] Диагностика завершена. Статус системы: {global_report['status']}")

        return global_report

    def save_and_respond(self, report: dict) -> None:
        print("[INFO] Оповещение респондеров и сохранение отчета")

        for responder in self._active_responders:
            try:
                responder.send_report(report)

            except Exception as e:
                print(f"[ERROR] Респондер не смог отправить отчет: {e}")
