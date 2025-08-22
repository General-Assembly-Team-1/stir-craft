# Procfile — Heroku / process manager configuration
# ---------------------------------------------------------------------------
# Purpose:
#  - Declare the process types for the application runtime used by Heroku
#    and some container/process managers.
#  - Each line follows the format: <process-type>: <command>
#  - The `web` process type is required by Heroku and receives HTTP traffic.
#
# How it works:
#  - Heroku will run the command after deploying your slug. The process must
#    bind to the port provided by the environment (Heroku sets $PORT).
#  - In Docker-based deployments you may not need a Procfile; it is harmless
#    to keep in the repository for platform portability.
#
# Common choices:
#  - Gunicorn (recommended for Django): "gunicorn <module>:application"
#  - Daphne / Uvicorn for async ASGI applications
#
# This project's minimal web process uses gunicorn and points to the Django
# WSGI application in `stircraft.wsgi`.

web: gunicorn stircraft.wsgi --log-file -

# Optional: you can add a worker process for background jobs, for example:
# worker: celery -A stircraft worker --loglevel=info
# (only add if you use Celery or a background worker)
