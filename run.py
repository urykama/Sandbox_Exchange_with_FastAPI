# run.py
import os
import sys

import uvicorn

from config import (
    PROJECT_NAME,
    VERSION,
    MODE,
    API_HOST,
    API_PORT,
    API_RELOAD,
    CANDLES_FOLDER,
    RESULTS_FOLDER,
)


def ensure_folders() -> None:
    os.makedirs(CANDLES_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)


def print_banner() -> None:
    line = "=" * 60
    print(line)
    print(f"  {PROJECT_NAME}")
    print(f"  Version: {VERSION}")
    print(f"  Mode:    {MODE}")
    print(line)
    print(f"  API:     http://{API_HOST}:{API_PORT}")
    print(f"  Docs:    http://127.0.0.1:{API_PORT}/docs")
    print(f"  Health:  http://127.0.0.1:{API_PORT}/health")
    print(line)
    print()


def main() -> None:
    ensure_folders()
    print_banner()

    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
    )


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()