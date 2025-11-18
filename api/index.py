"""WSGI entrypoint used by Vercel's Python runtime."""

from app import app as flask_app

# Vercel automatically looks for a WSGI callable named `app`
app = flask_app

