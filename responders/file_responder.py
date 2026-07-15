import os, sys, json
from typing import Dict, Any
from core.interfaces import ReportResponder


class FileResponder(ReportResponder):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def send_report(self, report: Dict[str, Any]) -> None:
        try:
            dir_name = os.path.dirname(self._file_path)

            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)

            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            print(f"[INFO] Отчет успешно сохранен в: {self._file_path}")

        except Exception as e:
            print(f"[ERROR] Не удалось записать отчет на диск: {e}")
