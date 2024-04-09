import sqlite3


# Function to create the database and tables
def create_database():
    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect("logging.db")
    c = conn.cursor()

    # Create table for guilds
    c.execute("""CREATE TABLE IF NOT EXISTS guilds (
                    guild_id INT PRIMARY KEY,
                    message_logs INT,
                    member_logs INT,
                    voice_logs INT,
                     mod_logs INT,
                     muterole INT,
                      muterole_channel INT
                      )""")

    # Commit changes and close connection
    conn.commit()
    conn.close()


create_database()
