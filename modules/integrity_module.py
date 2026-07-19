import os, hashlib
from typing import Dict, Any
from core.interfaces import DiagnosticModule


class IntegrityModule(DiagnosticModule):
    def __init__(self, name: str, mod_cfg: Dict[str, Any]):
        super().__init__(name)
        self._integrity_registry = mod_cfg.get("registry") or {}

    @staticmethod
    def _calculate_sha256(file_path: str) -> str:
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    @staticmethod
    def _check_existence(file_path: str) -> bool:
        return os.path.exists(file_path) if file_path else False

    @staticmethod
    def _verify_permissions(file_path: str, expected_perms: str) -> bool:
        try:
            current_perms = oct(os.stat(file_path).st_mode & 0o777)

            return current_perms == expected_perms

        except Exception:
            return False


    def _verify_checksums(self, file_path: str, expected_hash: str) -> bool:
        try:
            current_hash = self._calculate_sha256(file_path)

            return current_hash == expected_hash

        except Exception:
            return False


    def execute(self) -> Dict[str, Any]:
        components = {}
        has_errors = False

        if not self._integrity_registry:
            return {
                "status": "SUCCESS",
                "components": {},
            }

        for component_name, info in self._integrity_registry.items():
            file_path = info.get("path")
            expected_hash = info.get("sha256")
            expected_perms = info.get("permissions")

            component_report = {
                "path": file_path,
                "exists": False,
                "permissions_ok": False,
                "checksum_ok": False,
                "status": "FAILED",
            }

            if not file_path or not expected_hash or not expected_perms:
                components[component_name] = component_report
                has_errors = True
                continue

            exists = self._check_existence(file_path)
            if not exists:
                components[component_name] = component_report
                has_errors = True
                continue

            component_report["exists"] = True

            perms_ok = self._verify_permissions(file_path, expected_perms)
            hash_ok = self._verify_checksums(file_path, expected_hash)

            component_report["checksum_ok"] = hash_ok
            component_report["permissions_ok"] = perms_ok

            if hash_ok and perms_ok:
                component_report["status"] = "OK"
            else:
                has_errors = True

            components[component_name] = component_report

        return {
            "status": "FAILURE" if has_errors else "SUCCESS",
            "components": components
        }