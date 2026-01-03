from lib.query_executor.executors.sqlalchemy import SqlAlchemyQueryExecutor
from plugins.gsm_plugin.gsm_utils import patch_password_in_conn_str

class GSMSqlAlchemyQueryExecutor(SqlAlchemyQueryExecutor):
    @classmethod
    def _get_client(cls, client_setting):
        # Patch the connection string if GSM is used
        if 'connection_string' in client_setting:
            client_setting = dict(client_setting)
            client_setting['connection_string'] = patch_password_in_conn_str(client_setting['connection_string'])
        return super()._get_client(client_setting)

    @classmethod
    def EXECUTOR_NAME(cls):
        # Prefix GSM to the base executor name
        base_name = super().EXECUTOR_NAME() if hasattr(super(), 'EXECUTOR_NAME') else 'sqlalchemy'
        return f"GSM{base_name}"

    @classmethod
    def EXECUTOR_LANGUAGE(cls):
        # Inherit the language from the base class
        return super().EXECUTOR_LANGUAGE() if hasattr(super(), 'EXECUTOR_LANGUAGE') else ["mysql", "postgresql"]
