#!/bin/bash

ARGV0=$0 # Zero argument is shell command
ARGV1=$1 # First argument is temp folder during install
ARGV2=$2 # Second argument is Plugin-Name for scipts etc.
ARGV3=$3 # Third argument is Plugin installation folder
ARGV4=$4 # Forth argument is Plugin version
ARGV5=$5 # Fifth argument is Base folder of LoxBerry

echo "<INFO> Copy back existing config files"
cp -p -v -r /tmp/$ARGV1\_upgrade/config/$ARGV3/* $ARGV5/config/plugins/$ARGV3/ 

echo "<INFO> Remove temporary folders"
rm -r /tmp/$ARGV1\_upgrade

echo "<INFO> start Midea2Lox"
is_running() {
	/bin/ps -C "midea2lox.py" -opid= > /dev/null 2>&1
}

if is_running; then
    PID=`/bin/ps -C "midea2lox.py" -opid=`
    killall midea2lox.py
else
    echo "Starting Midea2Lox..."
if [ $EUID -eq 0 ]; then
    cd $ARGV1/data/plugins/$ARGV3
    su loxberry -c ./midea2lox.py > /dev/null 2>&1 &
else
    cd $ARGV1/data/plugins/$ARGV3
    ./midea2lox.py > /dev/null 2>&1 &
fi
fi

# Exit with Status 0
exit 0
