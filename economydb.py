import sqlite3

# Function to create a database and table if they don't exist
def create_database():
    conn = sqlite3.connect('economy.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS members
                 (user_id INTEGER PRIMARY KEY, coins INTEGER)''')
    conn.commit()
    conn.close()

# Create the database
create_database()
