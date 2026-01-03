from plugins.gsm_plugin.gsm_sqlalchemy_executor import GSMESqlAlchemyQueryExecutor
from plugins.gsm_plugin.gsm_sqlalchemy_metastore import GSMSqlAlchemyMetastoreLoader

# Optionally, you can provide a registration function if Querybook supports plugin auto-registration:
# def register():
#     return [GSMEnabledSqlAlchemyQueryExecutor, GSMEnabledSqlAlchemyMetastoreLoader]

# GSM Plugin for Querybook

# This package provides GSM-enabled executors and metastores for MySQL and PostgreSQL.
