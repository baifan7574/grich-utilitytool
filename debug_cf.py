import requests
import json

DEFAULT_ACCOUNT_ID = "c70f291b77fbc02a6f2090abe4abd44" 
ALT_ACCOUNT_ID = "c70f291b77fbc02a6f2090ebe4abdd44"
TOKEN = "uF8Fot3HVZ2ugZ7YWTmkTTaDlOAJ5KFoakCOQV2Z"

def check_account(acc_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/pages/projects"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Checking Account {acc_id}...")
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            projects = [p['name'] for p in data['result']]
            print("Projects Found:", projects)
            return True, projects
        else:
            print("Error:", response.text)
            return False, []
    except Exception as e:
        print("Exception:", e)
        return False, []

def create_project(acc_id):
    url = f"https://api.cloudflare.com/client/v4/accounts/{acc_id}/pages/projects"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "grich-utilitytool",
        "production_branch": "main"
    }
    print(f"Creating project 'quick-tools-hub' in account {acc_id}...")
    response = requests.post(url, headers=headers, json=payload)
    print("Creation Status:", response.status_code)
    print("Response:", response.text)

# Try default ID first
success, projects = check_account(DEFAULT_ACCOUNT_ID)
if not success:
    print("Retrying with alternate ID...")
    success, projects = check_account(ALT_ACCOUNT_ID)
    if success:
        active_id = ALT_ACCOUNT_ID
    else:
        print("Both IDs failed.")
        exit(1)
else:
    active_id = DEFAULT_ACCOUNT_ID

# Check if target exists
if "grich-utilitytool" not in projects:
    print("Project 'grich-utilitytool' MISSING. Creating it now...")
    create_project(active_id)
else:
    print("Project 'grich-utilitytool' ALREADY EXISTS.")
