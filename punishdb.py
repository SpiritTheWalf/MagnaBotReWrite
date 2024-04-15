import sqlite3

# Connect to the database
conn = sqlite3.connect('punishment_history.db')
c = conn.cursor()

# Create punishments table
c.execute('''CREATE TABLE IF NOT EXISTS punishments (
             id INTEGER PRIMARY KEY,
             guild_id INTEGER,
             user_id INTEGER,
             punishment_type TEXT,
             punishment_time TIMESTAMP,
             punisher_id INT,
             reason TEXT,
             FOREIGN KEY (guild_id) REFERENCES guilds(guild_id),
             FOREIGN KEY (user_id) REFERENCES users(user_id))''')

# Commit changes and close connection
conn.commit()
conn.close()
