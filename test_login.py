import sqlite3
import uuid
import os
from werkzeug.security import generate_password_hash
from app import app
from backend.db import init_db, get_db_connection

# Make sure db is initialized
init_db()

# Create a test user directly in the database
email = f"test_{uuid.uuid4().hex[:6]}@example.com"
password = "password123"

conn = get_db_connection()
conn.execute('INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)',
             ('Test User', email, generate_password_hash(password), 'candidate'))
conn.commit()
conn.close()

# Test login route
client = app.test_client()
response = client.post('/api/auth/login', json={'email': email, 'password': password})

print("Status:", response.status_code)
print("Data:", response.get_json())
