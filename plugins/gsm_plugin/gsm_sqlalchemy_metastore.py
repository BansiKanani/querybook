from lib.metastore.loaders.sqlalchemy_metastore_loader import SqlAlchemyMetastoreLoader
from plugins.gsm_plugin.gsm_utils import patch_password_in_conn_str

class GSMSqlAlchemyMetastoreLoader(SqlAlchemyMetastoreLoader):
    def __init__(self, metastore_dict):
        # Patch the connection string if GSM is used
        patched_dict = dict(metastore_dict)
        if 'connection_string' in patched_dict:
            patched_dict['connection_string'] = patch_password_in_conn_str(patched_dict['connection_string'])
        super().__init__(patched_dict)