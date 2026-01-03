# Querybook GSM Plugin

This plugin provides GSM-enabled Query Executors and Metastore Loaders for MySQL and PostgreSQL in Querybook, allowing you to securely fetch database passwords from Google Secret Manager (GSM) at runtime.

## Motivation

- **Security**: Prevents admins and users from seeing plaintext DB passwords in Querybook configs.
- **Convenience**: Use a GSM path in your connection string, and the plugin will fetch the secret dynamically.

## Usage


### 2. Configure Querybook

In your Querybook DB connection config, use a GSM path for the password:

```
mysql+pymysql://<DB_USER>:gsm://projects/<PROJECT_ID>/secrets/<SECRET_ID>/versions/<VERSION_ID>@<DB_HOST>:<DB_PORT>

postgresql+psycopg2://<DB_USER>:gsm://projects/<PROJECT_ID>/secrets/<SECRET_ID>/versions/<VERSION_ID>@<DB_HOST>:<DB_PORT>/<DATABASE_NAME>
```

- The plugin will detect the `gsm://` prefix and fetch the password from Google Secret Manager.

### 3. Use the GSM Executors and Metastore Loaders

- For MySQL/PostgreSQL:
  - Executor: `GSMQueryExecutor`
  - Metastore Loader: `GSMMetastoreLoader`

### 4. Example Config

```
# QueryEngine config
Name = my-mysql-gsm
Executor = GSMQueryExecutor
Metastore = my-mysql-gsm-metastore
Connection_string = mysql+pymysql://user:gsm://projects/myproj/secrets/mysqlpass/versions/1@host:3306

# Metastore config
Name = my-mysql-gsm-metastore
Loader = GSMMetastoreLoader
Connection_string = mysql+pymysql://user:gsm://projects/myproj/secrets/mysqlpass/versions/1@host:3306
```

## How it Works

- The plugin inspects the connection string for a password starting with `gsm://`.
- It fetches the secret from Google Secret Manager and patches the connection string before use.

## Testing

See `test_gsm_plugin.py` for test cases.

## Requirements
- `google-cloud-secret-manager` Python package
- Google Cloud credentials with access to the secret

## Security
- Passwords are never stored or logged in plaintext.
- Only the GSM path is visible in configs.

---

**Note:** This plugin does not modify Querybook core code. It only extends via inheritance and can be safely used in private deployments.
