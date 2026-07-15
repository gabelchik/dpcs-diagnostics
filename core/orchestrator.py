import sys, json, datetime
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
                    self._active_modules.append(klass(mod_key, mod_cfg.get("limits", {})))
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

    def run(self) -> None:
        if not self._active_modules:
            print("[WARNING] Нет активных модулей для запуска")
            return

        print(f"[INFO] Запуск диагностики...")
        global_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "OK",
            "results": {}
        }

        for module in self._active_modules:
            try:
                module_report = module.execute()
                global_report["results"][module.name] = module_report

                if module_report.get("status") == "CRITICAL" and global_report.get("status") == "OK":
                    global_report["status"] = "CRITICAl"

            except Exception as e:
                print(f"[ERROR] Ошибка при работе модуля {module.name}: {e}")
                global_report["reports"][module.name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                if global_report.get("status") == "OK":
                    global_report["status"] = "CRITICAL"

        print(f"[INFO] Диагностика завершена. Статус системы: {global_report['status']}")
        for responder in self._active_responders:
            try:
                responder.send_report(global_report)

            except Exception as e:
                print(f"[ERROR] Респондер не смог отправить отчет: {e}")