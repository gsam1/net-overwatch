#/bin/bash
echo "Setting Environment Variables"
echo "NMONITOR=$(dirname $(pwd))" >> /etc/environment
export NMONITOR=$(dirname $(pwd))