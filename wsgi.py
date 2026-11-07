"""
WSGI Production Entrypoint for Apex Federal Bank Web Portal.
Compatible with Gunicorn, Waitress, uWSGI, Render, Railway, and PythonAnywhere.
"""

from web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
