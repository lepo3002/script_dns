import requests
import json
import os
import time

# Configuration (can be set as environment variables or directly in the script)
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "cwBF9ciCQCLW4gQ0uVVMe0crJ9QDN6NV2CbDNKdJ")
ZONE_ID = os.environ.get("ZONE_ID", "959d5297a5bde23f94ae66e887e48235")
RECORDS = [
    {"id": "35220d5956e78d259d6b4fb5234fa132", "name": "panel.olielectroempire.ca"},
    {"id": "ee47c96fbcc71909741b0d3428e4be2f", "name": "mc.olielectroempire.ca"}
]
# DNS_RECORD_ID_PANEL = os.environ.get("DNS_RECORD_ID_PANEL", "35220d5956e78d259d6b4fb5234fa132")
# DNS_RECORD_ID_MC = os.environ.get("DNS_RECORD_ID_MC", "ee47c96fbcc71909741b0d3428e4be2f")
RECORD_TYPE = os.environ.get("RECORD_TYPE", "A") # Can be A or AAAA
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", 300)) # Check every 5 minutes

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json()["ip"]
    except requests.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

def get_dns_record_ip(record_id):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["result"]["content"]
    except requests.RequestException as e:
        print(f"Error getting DNS record: {e}")
        return None

# def get_dns_record_id(record_name, zone_id, api_token):
#     url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={record_name}"
#     headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         records = response.json()["result"]
#         if records:
#             return records[0]["id"]
#         else:
#             print(f"DNS record with name '{record_name}' not found.")
#             return None
#     except requests.exceptions.RequestException as e:
#          print(f"Error retrieving DNS record ID: {e}")
#          return None

# def update_dns_record(ip_address, record_id, zone_id, record_type, api_token, dns_record_name):
#     url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
#     headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
#     payload = {"type": record_type, "name": dns_record_name, "content": ip_address, "ttl": 120, 'proxied': True}
#     try:
#         response = requests.put(url, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         return response.json()["success"]
#     except requests.exceptions.RequestException as e:
#         print(f"Error updating DNS record: {e}")
#         return False

def update_dns_record_ip(record_id, record_name, new_ip):
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    data = {
        "type": "A",
        "name": record_name,
        "content": new_ip,
        "ttl": 1,
        "proxied": False
    }
    try:
        response = requests.put(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"Updated DNS record {record_name} to IP: {new_ip}")
    except requests.RequestException as e:
        print(f"Error updating DNS record {record_id}: {e}")
    
def main_loop():
    last_ip = None
    while True:
        current_ip = get_public_ip()
        if current_ip and current_ip != last_ip:
            for record in RECORDS:
                dns_ip = get_dns_record_ip(record["id"])
                if current_ip != dns_ip:
                    update_dns_record_ip(record["id"], record["name"], current_ip)
                else:
                    print(f"No update needed for {record['name']}. IP unchanged.")
            last_ip = current_ip
        else:
            print("IP unchanged or unable to fetch IP.")
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main_loop()