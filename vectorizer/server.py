from app.service import serve
from app.logs import app_logger

if __name__ == "__main__":
    app_logger.info(f"Starting gRPC service")
    try:
        serve()

    except KeyboardInterrupt:
        app_logger.info("Stopping gRPC service")
