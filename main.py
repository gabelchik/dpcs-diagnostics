from core.orchestrator import DiagnosticCore


def main():
    print("[INFO] Запуск утилиты диагностики РСУ ТП")

    core = DiagnosticCore()
    core.run()

    print("[INFO] Ядро успешно запущено.")


if __name__ == "__main__":
    main()