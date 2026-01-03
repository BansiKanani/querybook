import re
from typing import Optional

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None

GSM_PREFIX = "gsm://"


def extract_gsm_path(password: str) -> Optional[str]:
    if password.startswith(GSM_PREFIX):
        return password[len(GSM_PREFIX):]
    return None


def fetch_gsm_secret(gsm_path: str) -> str:
    if secretmanager is None:
        raise ImportError("google-cloud-secret-manager is not installed.")
    # gsm_path: projects/<PROJECT_ID>/secrets/<SECRET_ID>/versions/<VERSION_ID>
    pattern = r"projects/([^/]+)/secrets/([^/]+)/versions/([^/]+)"
    match = re.match(pattern, gsm_path)
    if not match:
        raise ValueError(f"Invalid GSM path: {gsm_path}")
    project_id, secret_id, version_id = match.groups()
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def patch_password_in_conn_str(conn_str: str) -> str:
    """
    If the password in the connection string is a GSM path, fetch the secret and replace it.
    """
    # Regex to match connection string with password
    # e.g. mysql+pymysql://user:password@host:port/db
    pattern = r"(\w+\+\w+://[^:]+:)([^@]+)(@.+)"
    match = re.match(pattern, conn_str)
    if not match:
        return conn_str
    prefix, password, suffix = match.groups()
    gsm_path = extract_gsm_path(password)
    if gsm_path:
        real_password = fetch_gsm_secret(gsm_path)
        return f"{prefix}{real_password}{suffix}"
    return conn_str
