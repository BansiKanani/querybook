# from lib.query_executor.base_executor import QueryExecutorBaseClass
from .gsm_sqlalchemy_executor import GSMSqlAlchemyQueryExecutor


ALL_PLUGIN_EXECUTORS = [
    GSMSqlAlchemyQueryExecutor,
]
