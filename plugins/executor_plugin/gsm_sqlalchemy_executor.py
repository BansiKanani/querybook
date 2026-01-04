from lib.query_executor.executors.sqlalchemy import SqlAlchemyQueryExecutor
import re
from typing import Optional
import subprocess
import sys
import os


GSM_PREFIX = "gsm://"


    
def fetch_gsm_secret_in_subprocess(gsm_path):
    script_path = os.path.join(os.path.dirname(__file__), "gsm_fetch_worker.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = "/opt/querybook"
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
        new_conn_string = f"{prefix}{real_password}{suffix}"
        print(f"yooo returning actual string: {new_conn_string}")
        return f"{new_conn_string}"
    print(f"returning conn_str: {conn_str}")
    return conn_str




class GSMSqlAlchemyQueryExecutor(SqlAlchemyQueryExecutor):
    @classmethod
    def _get_client(cls, client_setting):
        print("yooo get_client of GSMSqlAlchemyQueryExecutor")
        # Patch the connection string if GSM is used
        if 'connection_string' in client_setting:
            client_setting = dict(client_setting)
            client_setting['connection_string'] = patch_password_in_conn_str(client_setting['connection_string'])
        return super()._get_client(client_setting)

    @classmethod
    def EXECUTOR_NAME(cls):
        return f"GSMsqlalchemy"

    @classmethod
    def EXECUTOR_LANGUAGE(cls):
        return ["mysql", "postgresql"]