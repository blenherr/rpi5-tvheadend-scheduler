#!/bin/sh

FILENAME="tvh-scheduler"
DIRNAME=$(dirname "$(realpath $0)")
TEMP_DIR=$(mktemp -d)

# Create $TEMP_DIR/$FILENAME.service
echo "Create $TEMP_DIR/$FILENAME.service"
echo "[Unit]" > $TEMP_DIR/$FILENAME.service
echo "Description=Auto poweroff Raspberry Pi 5 and wake for a recording" >> $TEMP_DIR/$FILENAME.service
echo "After=tvheadend.service" >> $TEMP_DIR/$FILENAME.service
echo "Requires=tvheadend.service" >> $TEMP_DIR/$FILENAME.service
echo "" >> $TEMP_DIR/$FILENAME.service
echo "[Service]" >> $TEMP_DIR/$FILENAME.service
echo "Type=simple" >> $TEMP_DIR/$FILENAME.service
echo "User=$USER" >> $TEMP_DIR/$FILENAME.service
echo "Group=$USER" >> $TEMP_DIR/$FILENAME.service
echo "ExecStart=/usr/bin/python $DIRNAME/$FILENAME.py" >> $TEMP_DIR/$FILENAME.service
echo "WorkingDirectory=$DIRNAME" >> $TEMP_DIR/$FILENAME.service
echo "Restart=on-failure" >> $TEMP_DIR/$FILENAME.service
echo "RestartSec=10" >> $TEMP_DIR/$FILENAME.service
echo "" >> $TEMP_DIR/$FILENAME.service
echo "[Install]" >> $TEMP_DIR/$FILENAME.service
echo "WantedBy=multi-user.target" >> $TEMP_DIR/$FILENAME.service

# Copy service file
echo "Copy $TEMP_DIR/$FILENAME.service to /lib/systemd/system/$FILENAME.service"
sudo cp $TEMP_DIR/$FILENAME.service /lib/systemd/system/$FILENAME.service

# Enable service
echo "Enable $FILENAME.service"
sudo systemctl enable $FILENAME.service

# Start service
echo "Start $FILENAME.service"
sudo systemctl restart $FILENAME.service

# Reload deamon
echo "Reload deamon"
sudo systemctl daemon-reload

# Done
echo "Done!"
