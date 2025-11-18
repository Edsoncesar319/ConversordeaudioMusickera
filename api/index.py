"""Vercel entrypoint exposing the Flask app as a WSGI handler."""

from vercel_wsgi import handle
from app import app


def handler(request, context):
    """WSGI-compatible handler required by Vercel."""
    return handle(request, context, app)

