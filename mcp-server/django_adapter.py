import os

import requests


API_ROOTS = [
    os.getenv("PROTZILLA_API_URL", "http://127.0.0.1:8000/api"),
    "http://localhost:5173/api",
]

# One session per API root so the CSRF cookie and token stay paired.
_sessions: dict[str, requests.Session] = {}
_csrf_tokens: dict[str, str] = {}


def _url(api_root: str, endpoint: str) -> str:
    return f"{api_root.rstrip('/')}/{endpoint.strip('/')}/"


def _session(api_root: str) -> requests.Session:
    if api_root not in _sessions:
        _sessions[api_root] = requests.Session()
    return _sessions[api_root]


def _csrf_token(api_root: str, *, refresh: bool = False) -> str:
    """Fetch Django's CSRF token; the session keeps the matching cookie."""
    if refresh or api_root not in _csrf_tokens:
        response = _session(api_root).get(_url(api_root, "get_csrf_token"))
        response.raise_for_status()
        _csrf_tokens[api_root] = response.json()["csrfToken"]
    return _csrf_tokens[api_root]


def _post_with_csrf(api_root: str, endpoint: str, data: dict) -> requests.Response:
    session = _session(api_root)
    response = session.post(
        _url(api_root, endpoint),
        json=data,
        headers={"X-CSRFToken": _csrf_token(api_root)},
    )
    if response.status_code == 403:
        # Token/cookie may be stale (e.g. Django restarted); retry once.
        response = session.post(
            _url(api_root, endpoint),
            json=data,
            headers={"X-CSRFToken": _csrf_token(api_root, refresh=True)},
        )
    return response


def post(endpoint: str, *, allow_error_data: bool = False, **data) -> dict:
    connection_error = None
    for api_root in dict.fromkeys(API_ROOTS):
        try:
            response = _post_with_csrf(api_root, endpoint, data)
            result = response.json()
        except requests.ConnectionError as error:
            connection_error = error
            continue
        except ValueError as error:
            raise ValueError(
                f"Django returned an invalid response (HTTP {response.status_code})."
            ) from error

        if result.get("success"):
            return result.get("data", {})
        if allow_error_data and result.get("data"):
            return result["data"]

        message = result.get("message", response.text)
        if isinstance(message, dict):
            message = message.get("msg", str(message))
        raise ValueError(message)

    raise ValueError(
        "Could not reach the PROTzilla Django API. :("
    ) from connection_error
