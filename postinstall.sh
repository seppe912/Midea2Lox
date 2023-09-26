#!/bin/bash

# Shell script which is executed by bash *AFTER* complete installation is done
# (but *BEFORE* postupdate). Use with caution and remember, that all systems may
# be different!
#
# Exit code must be 0 if executed successfull. 
# Exit code 1 gives a warning but continues installation.
# Exit code 2 cancels installation.
#
# Will be executed as user "loxberry".
#
# You can use all vars from /etc/environment in this script.
#
# We add 5 additional arguments when executing this script:
# command <TEMPFOLDER> <NAME> <FOLDER> <VERSION> <BASEFOLDER>
#
# For logging, print to STDOUT. You can use the following tags for showing
# different colorized information during plugin installation:
#
# <OK> This was ok!"
# <INFO> This is just for your information."
# <WARNING> This is a warning!"
# <ERROR> This is an error!"
# <FAIL> This is a fail!"

# To use important variables from command line use the following code:
COMMAND=$0    # Zero argument is shell command
PTEMPDIR=$1   # First argument is temp folder during install
PSHNAME=$2    # Second argument is Plugin-Name for scipts etc.
PDIR=$3       # Third argument is Plugin installation folder
PVERSION=$4   # Forth argument is Plugin version
#LBHOMEDIR=$5 # Comes from /etc/environment now. Fifth argument is
              # Base folder of LoxBerry
PTEMPPATH=$6  # Sixth argument is full temp path during install (see also $1)

# Combine them with /etc/environment
PCGI=$LBPCGI/$PDIR
PHTML=$LBPHTML/$PDIR
PTEMPL=$LBPTEMPL/$PDIR
PDATA=$LBPDATA/$PDIR
PLOG=$LBPLOG/$PDIR # Note! This is stored on a Ramdisk now!
PCONFIG=$LBPCONFIG/$PDIR
PSBIN=$LBPSBIN/$PDIR
PBIN=$LBPBIN/$PDIR

ARGV2=$2 # Second argument is real Plugin name
ARGV3=$3 # Third argument is Plugin installation folder
ARGV5=$5 # Fifth argument is Base folder of LoxBerry

chmod +x $PDATA/midea2lox.py
chmod +x $PDATA/discover.py

# Installing Python requirements in Virtual enviroment
python3 -m venv $PBIN/venv

source $PBIN/venv/bin/activate

pip3 install --upgrade pip
pip3 install --upgrade pip setuptools wheel
pip3 install requests --extra-index-url https://www.piwheels.org/simple --prefer-binary
pip3 install paho-mqtt --extra-index-url https://www.piwheels.org/simple --prefer-binary
pip3 install ifaddr --extra-index-url https://www.piwheels.org/simple --prefer-binary
pip3 install msmart-ng==2023.9.5 --extra-index-url https://www.piwheels.org/simple --prefer-binary

deactivate

/bin/echo "#############################################################################################"
/bin/echo "#  Nach der Installation bitte die Einstellungen zu allen MiniServern anpassen und speichern."
/bin/echo "#  Danach den Service starten."
/bin/echo "#############################################################################################"

# Exit with Status 0
exit 0
