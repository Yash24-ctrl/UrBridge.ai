import sqlite3

# Connect to database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# Check if users table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = c.fetchone()

if table_exists:
    print("✅ Users table exists")
    # Get user count
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    print(f"👥 Total users: {count}")
    
    # Show first 5 users
    c.execute("SELECT id, username, email FROM users LIMIT 5")
    users = c.fetchall()
    if users:
        print("\n📋 Users in database:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    else:
        print("⚠️ No users found in database")
else:
    print("❌ Users table does not exist")

conn.close()