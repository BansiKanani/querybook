import sys
import re

try:
    from google.cloud import secretmanager
except ImportError:
    secretmanager = None

def fetch_gsm_secret(gsm_path: str) -> str:
    # print("yooo fetching the secret from gsm: ", gsm_path)
    if secretmanager is None:
        raise ImportError("google-cloud-secret-manager is not installed.")
    # gsm_path: projects/<PROJECT_ID>/secrets/<SECRET_ID>/versions/<VERSION_ID>
    pattern = r"projects/([^/]+)/secrets/([^/]+)/versions/([^/]+)"
    match = re.match(pattern, gsm_path)
    if not match:
        raise ValueError(f"Invalid GSM path: {gsm_path}")
    project_id, secret_id, version_id = match.groups()
    client = secretmanager.SecretManagerServiceClient()
    # print("yooo GSM client initialized")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    # print("yooo trying to fetch secret:", name)
    response = client.access_secret_version(request={"name": name})
    # print("yooo got response from GSM:", response)
    return response.payload.data.decode("UTF-8")



if __name__ == "__main__":
    gsm_path = sys.argv[1]
    try:
        print(fetch_gsm_secret(gsm_path), end="")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
