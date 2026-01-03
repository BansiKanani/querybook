import unittest
from unittest.mock import patch, MagicMock
from plugins.gsm_plugin import gsm_utils

class TestGSMUtils(unittest.TestCase):
    def test_extract_gsm_path(self):
        self.assertEqual(
            gsm_utils.extract_gsm_path("gsm://projects/p/secrets/s/versions/1"),
            "projects/p/secrets/s/versions/1",
        )
        self.assertIsNone(gsm_utils.extract_gsm_path("notgsm://foo"))

    @patch("plugins.gsm_plugin.gsm_utils.secretmanager")
    def test_fetch_gsm_secret(self, mock_secretmanager):
        mock_client = MagicMock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "mypassword"
        mock_client.access_secret_version.return_value = mock_response
        secret = gsm_utils.fetch_gsm_secret("projects/p/secrets/s/versions/1")
        self.assertEqual(secret, "mypassword")

    @patch("plugins.gsm_plugin.gsm_utils.fetch_gsm_secret")
    def test_patch_password_in_conn_str(self, mock_fetch):
        mock_fetch.return_value = "realpass"
        conn_str = "mysql+pymysql://user:gsm://projects/p/secrets/s/versions/1@host:3306/db"
        patched = gsm_utils.patch_password_in_conn_str(conn_str)
        self.assertIn(":realpass@host", patched)
        # Should not patch if not GSM
        conn_str2 = "mysql+pymysql://user:plainpass@host:3306/db"
        self.assertEqual(gsm_utils.patch_password_in_conn_str(conn_str2), conn_str2)

if __name__ == "__main__":
    unittest.main()
