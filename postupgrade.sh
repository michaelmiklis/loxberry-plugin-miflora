#!/bin/sh

# Bash script which is executed in case of an update (if this plugin is already
# installed on the system). This script is executed as very last step (*AFTER*
# postinstall) and can be for example used to save back or convert saved
# userfiles from /tmp back to the system. Use with caution and remember, that
# all systems may be different!
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

echo "<INFO> Copy back existing config files"
cp -v -r /tmp/uploads/$PTEMPDIR\_upgrade/config/$PDIR/* $PTEMPPATH/config/plugins/$PDIR/ 

echo "<INFO> Adding new config parameters"
grep -q -F "UDPENABLED=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "UDPENABLED=1" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg 
grep -q -F "MQTTENABLED=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTENABLED=0" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg
grep -q -F "MQTTBROKER=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTBROKER=localhost" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg
grep -q -F "MQTTPORT=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTPORT=1883" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg
grep -q -F "MQTTTOPIC=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTTOPIC=miflora" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg
grep -q -F "MQTTUSERNAME=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTUSERNAME=loxberry" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg
grep -q -F "MQTTPASSWORD=" $ARGV5/config/plugins/$ARGV3/miflora.cfg || echo "MQTTPASSWORD=secretPassword" >> $ARGV5/config/plugins/$ARGV3/miflora.cfg

echo "<INFO> Copy back existing log files"
cp -v -r /tmp/uploads/$PTEMPDIR\_upgrade/log/$PDIR/* $PTEMPPATH/log/plugins/$PDIR/ 

echo "<INFO> Remove temporary folders"
rm -r /tmp/uploads/$PTEMPDIR\_upgrade


# Replace real subfolder and scriptname
#/bin/sed -i "s#PLUGINDATAFOLDER#$PDATA#" $LBHOMEDIR/bin/plugins/$PDIR/miflora.py
#/bin/sed -i "s#PLUGINCONFIGFOLDER#$PCONFIG#" $LBHOMEDIR/bin/plugins/$PDIR/miflora.py
#/bin/sed -i "s#SYSTEMCONFIGFOLDER#$LBSCONFIG#" $LBHOMEDIR/bin/plugins/$PDIR/miflora.py

/bin/sed -i "s#PLUGINBINFOLDER#$LBHOMEDIR/bin/plugins/$PDIR#" $LBHOMEDIR/system/cron/cron.hourly/$PSHNAME

exit 0
