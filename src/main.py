
#!/usr/bin/python
import sqlite3
from datetime import datetime
import nvsmi
import pwd
import daemon
import time

month_array = ['jan_hours', 'feb_hours', 'mar_hours', 'apr_hours', 'may_hours', 'jun_hours', 'jul_hours', 'aug_hours', 'sep_hours', 'oct_hours', 'nov_hours', 'dec_hours']

# Set the polling interval (hours)
POLLING_INTERVAL_HOURS = 0.1
# DB Location - wherever you put this, the user being used to run the daemon must have access
DB_FILE = '/path/to/daemon/nvidialog.db'
LOG_FILE = '/tmp/daemon_log.txt'

def get_owner_linux(pid):
    try:
        with open(f'/proc/{pid}/status', 'r') as f:
            for line in f:
                if line.startswith('Uid:'):
                    uid = int(line.split()[1])
                    return pwd.getpwuid(uid).pw_name
    except FileNotFoundError:
        return None
    return None

def add_user(USER):
    DATE = str(datetime.now().date())
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    # Attempt to create the users table (if it doesn't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            date_updated TEXT,
            total_hours REAL,
            jan_hours REAL,
            feb_hours REAL,
            mar_hours REAL,
            apr_hours REAL,
            may_hours REAL,
            jun_hours REAL,
            jul_hours REAL,
            aug_hours REAL,
            sep_hours REAL,
            oct_hours REAL,          
            nov_hours REAL,          
            dec_hours REAL          
        )
    ''')

    # Attempt to create the user
    try:
        cursor.execute("INSERT INTO users (id, date_updated, total_hours, jan_hours, feb_hours, mar_hours, apr_hours, may_hours, jun_hours, jul_hours, aug_hours, sep_hours, oct_hours, nov_hours, dec_hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (USER, DATE, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        connection.commit()
    except:
        connection.close()


def add_time_to_user(USER, TIME):
    current_date = str(datetime.now().date())
    current_month = datetime.now().month
    month_table_field = month_array[current_month-1]
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(f"SELECT total_hours, {month_table_field} FROM users WHERE id = '{USER}'")
    query_hours = cursor.fetchall()
    total_hours = query_hours[0][0] + TIME
    month_hours = query_hours[0][1] + TIME
    # Update the hours and the modified date
    cursor.execute(f"UPDATE users SET date_updated = '{current_date}' WHERE id = '{USER}'")
    cursor.execute(f"UPDATE users SET total_hours = '{total_hours}' WHERE id = '{USER}'")
    cursor.execute(f"UPDATE users SET {month_table_field} = '{month_hours}' WHERE id = '{USER}'")
    # In a somewhat strange design choice - set the next month's hours to 0.
    # By doing this, we always keep relevant, fresh data. 11 months of it.
    if current_month == 12:
        next_month = 1
    else:
        next_month = current_month+1
    next_month_table_field = month_array[next_month-1]
    cursor.execute(f"UPDATE users SET {next_month_table_field} = '{0.0}' WHERE id = '{USER}'")
    connection.commit()
    connection.close()    


def run_daemon():
    while True:
        with open(LOG_FILE, "a") as f:
            f.write(f"{ str(datetime.now())} Polling NVIDIA\n")
            try:
                gpu_processes = nvsmi.get_gpu_processes()
                for process in gpu_processes:
                    print(process.pid)
                    process_owner = get_owner_linux(process.pid)
                    print(f"Process owner = {process_owner}")
                    # Add this user
                    add_user(process_owner)
                    # Add time to this
                    add_time_to_user(process_owner, POLLING_INTERVAL_HOURS)
            except:
                    f.write(f"{ str(datetime.now())} ERROR: Failed to process NVIDIA data\n")
            # Log
            f.write(f"{ str(datetime.now())} Preparing to sleep for {POLLING_INTERVAL_HOURS*60*60} seconds\n")
            time.sleep(POLLING_INTERVAL_HOURS*60*60)

if __name__ == "__main__":
    print("Starting Daemon")
    with daemon.DaemonContext():
       run_daemon()
