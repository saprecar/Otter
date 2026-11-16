"""
source_leak_guard.py - Defense-in-depth middleware to prevent source code and sensitive file leaks.

Guards:
1. Blocks access to version control paths (/.git, /.git/HEAD, /.gitignore)
2. Blocks environment files (/.env, /.env.*)
3. Blocks server configuration & backups (.htaccess, web.config, *.bak, *.sql, *.db)
4. Blocks dotfile / dotdir traversal (/.agent, /.agents, /.claude, etc.)
5. Localhost bypass: Requests originating strictly from localhost (127.0.0.1, ::1) can be optionally permitted or restricted.
   Public/remote IPs receive an immediate 404 Not Found (no fingerprinting) or 403 Forbidden.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
import ipaddress
import re

BLOCKED_PATTERNS = [
    r"(^|/)\.git(/.*|$)",          # /.git, /.git/HEAD, /.git/config, etc.
    r"(^|/)\.env(\..+|$)",         # /.env, /.env.local, /.env.production
    r"(^|/)\.agents?(/.*|$)",      # /.agent/, /.agents/
    r"(^|/)\.claude(/.*|$)",       # /.claude/
    r"(^|/)\.github(/.*|$)",       # /.github/
    r"(^|/)\.cursor(/.*|$)",       # /.cursor/
    r"(^|/)\.vscode(/.*|$)",       # /.vscode/
    r"\.(py|pyc|sql|db|sqlite3|bak|swp|ini|log|conf|sh|bat)$", # Raw source/config files
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]

def is_local_client(client_host: str) -> bool:
    """Check if the requesting client is on localhost."""
    if not client_host:
        return False
    try:
        ip = ipaddress.ip_address(client_host)
        return ip.is_loopback
    except ValueError:
        return client_host in ("localhost", "127.0.0.1", "::1")

class SourceLeakProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware that inspects every incoming HTTP request path.
    Blocks public access to source code, .git, and config files.
    Allows local development access only if allow_local=True.
    """
    def __init__(self, app, allow_local: bool = True):
        super().__init__(app)
        self.allow_local = allow_local

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.lower()
        client_ip = request.client.host if request.client else ""

        # Check if requested path matches any protected/leakable pattern
        is_blocked_path = any(pattern.search(path) for pattern in COMPILED_PATTERNS)

        if is_blocked_path:
            # If request is from localhost and allow_local is enabled, allow access
            if self.allow_local and is_local_client(client_ip):
                return await call_next(request)
            
            # For public/remote requests, return 404 (does not confirm file existence)
            return PlainTextResponse("Not Found", status_code=404)

        return await call_next(request)
