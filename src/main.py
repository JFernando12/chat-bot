import logging
import uvicorn
from api.fastapi_app import create_app

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

def main():
    configure_logging()
    app = create_app()
    logging.info("Iniciando agente (LangGraph + FastAPI)")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )

if __name__ == "__main__":
    main()
