#!/usr/bin/env bash

DEAMONNAME="rpi5-tvheadend-scheduler"
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_FILE="$DEAMONNAME.service"

# Create service file
echo "Create $SERVICE_FILE file:"
echo ""
echo "[Unit]" | sudo tee $SCRIPT_DIR"/"$SERVICE_FILE
echo "Description=Auto poweroff Raspberry Pi 5 and wake for a recording" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "After=tvheadend.service" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "Requires=tvheadend.service" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "[Service]" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "Type=simple" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "User=$USER" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "Group=$USER" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "ExecStart=/usr/bin/python "$SCRIPT_DIR"/"$DEAMONNAME".py" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "Restart=on-failure" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "RestartSec=10" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "[Install]" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo "WantedBy=multi-user.target" | sudo tee -a $SCRIPT_DIR"/"$SERVICE_FILE
echo ""

# Copy service file
echo "Copy $SERVICE_FILE to /lib/systemd/system/$SERVICE_FILE"
sudo cp $SCRIPT_DIR"/"$SERVICE_FILE /lib/systemd/system/$SERVICE_FILE

# Enable service
echo "Enable $DEAMONNAME service"
sudo systemctl enable $DEAMONNAME

# Start service
echo "Start $DEAMONNAME service"
sudo systemctl start $DEAMONNAME
