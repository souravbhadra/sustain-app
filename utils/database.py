import os
import pandas as pd
from deta import Deta
from dotenv import load_dotenv

# Load the environment variable
load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")

# Initialize with a project key
deta = Deta(DETA_KEY)

# Create/connect a database
db = deta.Base("sustain_users_3")

def insert_user(username, name, password):
    """Returns the user info"""
    return db.put({"key": username, "name": name, "password": password})

def fetch_all_users():
    """Returns a dictionary of all users"""
    res = db.fetch()
    return res.items

def update_user(username, updates):
    """If the item is updated, returns None. Otherwise an exception is raised"""
    return db.update(updates, username)

def delete_user(username):
    """Always returns None, even if the key does not exist"""
    return db.delete(username)