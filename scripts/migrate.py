import json
import csv
import requests
import sys

# --- CONFIGURATION ---
API_BASE_URL = ""
API_TOKEN = ""
SOURCE_JSON = "test.json"
MIGRATION_CSV = "migration_data.csv"
SECRETS_PROJECT = ""
BUSINESS_UNIT = ""
ENVIRONMENT = 1

HEADERS = {
    "api-access-token": API_TOKEN,
    "Content-Type": "application/json"
}

# --- UTILS ---

def clean_service_name(service_name):
    """Tokenizes string"""
    tokens = service_name.split('-')
    filtered = [t for t in tokens if t.lower() not in ['stg']]
    return "-".join(filtered).strip()

def get_gsm_path(password_secret_name):
    """Generates the Google Secret Manager path."""
    return f"gsm://projects/{SECRETS_PROJECT}/secrets/{password_secret_name}/versions/1"

# --- PART 1: CSV GENERATION ---

def generate_csv_from_json(input_file, output_file):
    print(f"Reading {input_file} and generating CSV...")
    
    with open(input_file, 'r') as f:
        data = json.load(f)

    rows = []

    # Process MySQL
    for item in data.get('mysql', []):
        service_cleaned = clean_service_name(item['service'])
        db_password = get_gsm_path(item['password'])
        db_host = item['proxy_host']
        db_port = item['proxy_port']
        db_user = item['username']
        
        # Connection string for MySQL
        conn_str = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}"
        
        rows.append({
            "business_unit": BUSINESS_UNIT,
            "type": "MySQL",
            "connection_string": conn_str,
            "q_metastore": f"mysql-{service_cleaned}",
            "q_query_engine": f"mysql-{service_cleaned}",
            "q_environment": ENVIRONMENT ,
        })

    # Process PostgreSQL
    for item in data.get('postgresql', []):
        service_cleaned = clean_service_name(item['service'])
        db_password = get_gsm_path(item['password'])
        db_host = item['domain']
        db_port = "5432" # Default PG port if not provided
        db_user = item['username']
        
        # Iterate over each database for Postgres
        for db_name in item.get('databases', []):
            conn_str = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            rows.append({
                "business_unit": BUSINESS_UNIT,
                "type": "Postgres",
                "connection_string": conn_str,
                "q_metastore": f"{db_name}-{service_cleaned}",
                "q_query_engine": f"{db_name}-{service_cleaned}",
                "q_environment": ENVIRONMENT,
            })

    # Write to CSV
    fieldnames = ["business_unit", "type", "connection_string", "q_metastore", "q_query_engine", "q_environment"]
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Successfully generated {output_file} with {len(rows)} entries.")

# --- PART 2: API MIGRATION ---

def run_api_migration(csv_file):
    print(f"Starting API migration from {csv_file}...")
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"\n--- Processing: {row['q_metastore']} ---")
            
            # 1. Create Metastore
            ms_payload = {
                "name": row['q_metastore'],
                "loader": "GSMSqlAlchemyMetastoreLoader",
                "metastore_params": {
                    "connection_string": row['connection_string'],
                    "connect_args": []
                },
                "acl_control": {}
            }
            
            ms_resp = requests.post(f"{API_BASE_URL}/query_metastore/", headers=HEADERS, json=ms_payload)
            if ms_resp.status_code != 200:
                print(f"Failed to create Metastore: {ms_resp.text}")
                continue
            
            metastore_id = ms_resp.json()['data']['id']
            print(f"Created Metastore ID: {metastore_id}")

            # 2. Create Query Engine
            qe_payload = {
                "name": row['q_query_engine'],
                "description": "Engine created via Script",
                "language": "postgresql" if row['type'] == "Postgres" else "mysql",
                "executor": "GSMsqlalchemy",
                "executor_params": {
                    "connection_string": row['connection_string']
                },
                "metastore_id": metastore_id,
                "feature_params": {
                    "status_checker": "ConnectionChecker", 
                    "upload_exporter": "SqlalchemyExporter"
                }
            }
            
            qe_resp = requests.post(f"{API_BASE_URL}/query_engine/", headers=HEADERS, json=qe_payload)
            if qe_resp.status_code != 200:
                print(f"Failed to create Engine: {qe_resp.text}")
                continue
            
            engine_id = qe_resp.json()['data']['id']
            print(f"Created Engine ID: {engine_id}")

            # 3. Add Engine to Environment
            env_id = row['q_environment']
            env_url = f"{API_BASE_URL}/environment/{env_id}/query_engine/{engine_id}/"
            env_resp = requests.post(env_url, headers=HEADERS, json={})
            
            # print(env_resp.json)

            if env_resp.status_code == 200:
                print(f"Successfully added Engine {engine_id} to Environment {env_id}")
            else:
                print(f"Failed to link to Env: {env_resp.text}")

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [csv|api|all]")
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "csv" or mode == "all":
        generate_csv_from_json(SOURCE_JSON, MIGRATION_CSV)
    
    if mode == "api" or mode == "all":
        run_api_migration(MIGRATION_CSV)