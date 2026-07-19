import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.orchestrator import DiagnosticCore


app = FastAPI(
    title="DPCS Diagnostics API",
    description="",
    version="1.0.0"
)


class PartialDiagnosticRequest(BaseModel):
    run_modules: Optional[List[str]] = None


@app.get("/api/v1/diagnostics")
def run_full_diagnostics():
    try:
        core = DiagnosticCore(config_path="./config.json")
        report = core.execute_diagnostics()
        core.save_and_respond(report)

        return report

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Файл конфигурации config.json не найден на узле"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при сборке диагностики: {str(e)}"
        )

@app.post("/api/v1/diagnostics/partial")
def run_partial_diagnostics(payload: PartialDiagnosticRequest):
    try:
        core = DiagnosticCore(config_path="./config.json")
        report = core.execute_diagnostics(target_modules=payload.run_modules)
        core.save_and_respond(report)

        return report

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Файл конфигурации config.json не найден на узле"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка при сборке частичной диагностики: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
