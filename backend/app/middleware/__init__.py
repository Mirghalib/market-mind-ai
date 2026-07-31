"""Custom ASGI middleware.

Pure ASGI middleware (no ContextVar, no request access). For Starlette
middleware that needs the request object (CORS, TrustedHost, GZip) use
`app.add_middleware(...)` from starlette.middleware in main.py instead.
"""
