#!/bin/sh

FILENAME="tvh-scheduler"

# Disable service
echo "Disable $FILENAME.service"
sudo systemctl disable $FILENAME.service

# Remove service
echo "Remove $FILENAME.service from /lib/systemd/system/"
sudo rm /lib/systemd/system/$FILENAME.service

# Reload deamon
echo "Reload deamon"
sudo systemctl daemon-reload

# Done
echo "Done!"
