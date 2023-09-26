#!/bin/bash

# Shell script which is executed by bash *BEFORE* installation is started
# (*BEFORE* preinstall and *BEFORE* preupdate). Use with caution and remember,
# that all systems may be different!
#
# Exit code must be 0 if executed successfull. 
# Exit code 1 gives a warning but continues installation.
# Exit code 2 cancels installation.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Will be executed as user "root".
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

echo -n "<INFO> Current working folder is: "
pwd
echo "<INFO> Command is: $COMMAND"
echo "<INFO> Temporary folder is: $PTEMPDIR"
echo "<INFO> (Short) Name is: $PSHNAME"
echo "<INFO> Installation folder is: $PDIR"
echo "<INFO> Plugin version is: $PVERSION"
echo "<INFO> Plugin CGI folder is: $PCGI"
echo "<INFO> Plugin HTML folder is: $PHTML"
echo "<INFO> Plugin Template folder is: $PTEMPL"
echo "<INFO> Plugin Data folder is: $PDATA"
echo "<INFO> Plugin Log folder (on RAMDISK!) is: $PLOG"
echo "<INFO> Plugin CONFIG folder is: $PCONFIG"

# Set required version
PYTHON_MAJOR=3
PYTHON_MINOR=9

# Get python references
PYTHON3_REF=$(which python$PYTHON_MAJOR.$PYTHON_MINOR | grep "/python$PYTHON_MAJOR.$PYTHON_MINOR")

install_python(){
    echo "No Python 3.9, start installing..."
	
	OPENSSL_VER=1.1.1w
	mkdir openssl
	cd openssl
	wget https://www.openssl.org/source/openssl-${OPENSSL_VER}.tar.gz
	tar xf openssl-${OPENSSL_VER}.tar.gz
	cd openssl-${OPENSSL_VER}
	./config zlib shared no-ssl3
	make -j4
	sudo make install
	cd ..
	cd ..
	
	sudo apt update && sudo apt upgrade
	sudo apt install libffi-dev libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl git
	sudo apt-get install libffi-dev
	wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
	tar -zxvf Python-3.9.16.tgz
	cd Python-3.9.16
	./configure --enable-optimizations --with-ssl-default-suites=openssl
	sudo make altinstall
	cd ..
	
	echo "<INFO> Chown all TMP files"
	pwd
	chown -R loxberry:loxberry *
}

python_ref(){
    local my_ref=$1
    echo $($my_ref -c 'import platform; major, minor, patch = platform.python_version_tuple(); print(major); print(minor);')
}

# Print success_msg/install_python according to the provided minimum required versions
check_version(){
    local major=$1
    local minor=$2
    local python_ref=$3
    [[ $major == $PYTHON_MAJOR && $minor == $PYTHON_MINOR ]] && echo found $python_ref || install_python
}

# Logic
if [[ ! -z $PYTHON3_REF ]]; then
    version=($(python_ref python$PYTHON_MAJOR.$PYTHON_MINOR))
    check_version ${version[0]} ${version[1]} $PYTHON3_REF
else
    # required Python is not installed...
    install_python
fi

# Exit with Status 0
exit 0
