from lib.metastore.loaders.sqlalchemy_metastore_loader import SqlAlchemyMetastoreLoader
import re
from typing import Optional
import subprocess
import sys
import os


GSM_PREFIX = "gsm://"


def fetch_gsm_secret_in_subprocess(gsm_path):
    script_path = os.path.join(os.path.dirname(__file__), "gsm_fetch_worker.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/querybook/querybook/server:/opt/querybook/plugins:/opt/querybook"
    result = subprocess.run(
        [sys.executable, script_path, gsm_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        print("GSM subprocess error:", result.stderr)
        raise RuntimeError(f"GSM fetch failed: {result.stderr}")
    if result.stderr:
        print("GSM subprocess warning:", result.stderr)
    return result.stdout



def extract_gsm_path(password: str) -> Optional[str]:
    if password.startswith(GSM_PREFIX):
        return password[len(GSM_PREFIX):]
    return None


def patch_password_in_conn_str(conn_str: str) -> str:
    """
    If the password in the connection string is a GSM path, fetch the secret and replace it.
    """
    print("yooo patching the password in connection string")
    # Regex to match connection string with password
    # e.g. mysql+pymysql://user:password@host:port/db
    pattern = r"(\w+\+\w+://[^:]+:)([^@]+)(@.+)"
    match = re.match(pattern, conn_str)
    if not match:
        return conn_str
    prefix, password, suffix = match.groups()
    print(f"yooo connection string prefix: {prefix}, password: {password}, suffix: {suffix}")
    gsm_path = extract_gsm_path(password)
    print(f"yooo gsm_path: {gsm_path}")
    if gsm_path:
        real_password = fetch_gsm_secret_in_subprocess(gsm_path)
        print(f"yooo real_password: {real_password}")
        print(f"yooo returning actual string: {prefix}{real_password}{suffix}")
        return f"{prefix}{real_password}{suffix}"
    print(f"returning conn_str: {conn_str}")
    return conn_str


class GSMSqlAlchemyMetastoreLoader(SqlAlchemyMetastoreLoader):
    def __init__(self, metastore_dict):
        print("yooo initing GSMSqlAlchemyMetastore Loader")
        print("metastore_dict", metastore_dict)
        patched_dict = dict(metastore_dict)
        # Patch inside metastore_params
        if 'metastore_params' in patched_dict and 'connection_string' in patched_dict['metastore_params']:
            patched_dict['metastore_params'] = dict(patched_dict['metastore_params'])
            patched_dict['metastore_params']['connection_string'] = patch_password_in_conn_str(
                patched_dict['metastore_params']['connection_string']
            )
        print("patched_dict", patched_dict)
        super().__init__(patched_dict)
