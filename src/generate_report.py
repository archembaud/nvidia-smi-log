import sqlite3
from datetime import datetime

def get_users():
    connection = sqlite3.connect('/path/to/daemon/nvidialog.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    connection.close()
    return rows

users = get_users()
DATE = str(datetime.now())
print("================ GPU USAGE REPORT ================")
print(f"        ----- {DATE} -----")
for user in users:
    print(user)
print("==================================================")