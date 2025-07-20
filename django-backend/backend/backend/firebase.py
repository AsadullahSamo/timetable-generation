import firebase_admin
from firebase_admin import credentials
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

def initialize_firebase():
    cred_path = os.path.join(BASE_DIR, 'firebase', 'service-account.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)