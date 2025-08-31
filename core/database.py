import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

def supabase_get(table: str, params: dict = None):
    resp = requests.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=headers, params=params)
    return resp

def supabase_post(table: str, data: dict):
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers={**headers, "Content-Type": "application/json"}, json=data)
    return resp

def supabase_patch(table: str, filters: str, data: dict):
    resp = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{filters}", headers={**headers, "Content-Type": "application/json"}, json=data)
    return resp

def supabase_delete(table: str, filters: str):
    resp = requests.delete(f"{SUPABASE_URL}/rest/v1/{table}?{filters}", headers=headers)
    return resp
