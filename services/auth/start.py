import uvicorn

from src.core.log import log_config

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        reload_dirs=["src"],
        access_log=False,
        log_config=log_config,
        # loop='uvloop',
        timeout_graceful_shutdown=0,
    )
