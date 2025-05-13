# Simple Nvidia logging tool

This very simple tool comes complete with two files:

* The main.py file, which is a daemon designed to be run as part of a systemd service. 
* The generate_report.py file, which generates a report of the usage statistics. It's very basic.

## Requirements

This code needs the following pip modules installed:

* nvsmi
* python-daemon

## Key Variables

The code includes a couple of key items:

* LOG_FILE: The log file is stored in this directory; currently the /tmp directory - which means it won't survive a reboot, but is good for debugging the daemon.
* DB_FILE: The actual DB is stored in the location refered to with this variable. Make sure whatever user is executing this daemon (by systemd) has access to this location. 

## Running the daemon as a service

To make this daemon run as a service, we need to create a service definition to store with the other systemd services.

```bash
cd /etc/systemd/system/
sudo nano nvidialog.service
```

A sample service configuration file is shown below - this will run the daemon as USERNAME, from a location we are assuming that user has access to:

```bash
[Unit]
Description=nvidialog
After=network.target

[Service]
User=USERNAME
Group=USERNAME
WorkingDirectory=/path/to/daemon
ExecStart=/path/to/daemon/main.py

[Install]
WantedBy=multi-user.target
```

### After service creation

Run these steps to set up the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nvidialog.service
sudo systemctl start nvidialog.service
```

### Check the status, stop the service

```bash
# Check the status
sudo systemctl status nvidialog.service
# Stop the service
sudo systemctl stop nvidialog.service
```