"""
Netlify Serverless Function Handler for Apex Federal Bank Flask Application.
Translates AWS Lambda/Netlify API Gateway events into WSGI requests.
"""

import base64
import io
import sys
from urllib.parse import urlencode

# Add parent directory to sys.path so modules resolve on Netlify
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from web.app import create_app

flask_app = create_app()


def handler(event, context):
    """Entrypoint called by Netlify serverless execution environment."""
    path = event.get("path", "/")
    # Strip /.netlify/functions/app prefix if passed by redirect
    if path.startswith("/.netlify/functions/app"):
        path = path[len("/.netlify/functions/app"):] or "/"

    http_method = event.get("httpMethod", "GET")
    headers = event.get("headers", {}) or {}
    query_params = event.get("queryStringParameters") or {}
    raw_body = event.get("body", "") or ""

    if event.get("isBase64Encoded"):
        body_bytes = base64.b64decode(raw_body)
    elif isinstance(raw_body, str):
        body_bytes = raw_body.encode("utf-8")
    else:
        body_bytes = b""

    environ = {
        "REQUEST_METHOD": http_method,
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": urlencode(query_params),
        "SERVER_NAME": "netlify.app",
        "SERVER_PORT": "443",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": io.BytesIO(body_bytes),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "CONTENT_LENGTH": str(len(body_bytes)),
    }

    if "content-type" in headers:
        environ["CONTENT_TYPE"] = headers["content-type"]
    if "content-length" in headers:
        environ["CONTENT_LENGTH"] = headers["content-length"]

    for k, v in headers.items():
        k_normalized = k.upper().replace("-", "_")
        if k_normalized not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            environ[f"HTTP_{k_normalized}"] = str(v)

    response_headers = []
    status_code = [200]

    def start_response(status, resp_hdrs, exc_info=None):
        status_code[0] = int(status.split()[0])
        response_headers.extend(resp_hdrs)

    response_chunks = list(flask_app(environ, start_response))
    response_body = b"".join(response_chunks)

    flat_headers = {}
    multi_headers = {}
    for k, v in response_headers:
        if k.lower() == "set-cookie":
            multi_headers.setdefault("Set-Cookie", []).append(v)
        else:
            flat_headers[k] = v

    result = {
        "statusCode": status_code[0],
        "headers": flat_headers,
        "body": response_body.decode("utf-8", errors="replace"),
    }
    if multi_headers:
        result["multiValueHeaders"] = multi_headers

    return result
