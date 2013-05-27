#!/bin/perl

###############################################################################
# This script will crawl the specified directory tree(s). For each file found,
# a fingerprint is generated and compared against the specified SQLite 
# database. Files that do not exist in the database are automatically added.
# When the fingerprint of the file and the one in the database differ, the
# "last modified" timestamp of the file is compared with the timestamp in
# the database. If the file is newer, the entry is updated. Otherwise the file
# is flagged as potentially damaged. Files that are in the database but no
# longer exist are flagged but not removed. To remove, see --prune.
###############################################################################

use strict;
use warnings;
use Getopt::Long;
use DateTime;
#use DateTime::Format::Strptime;
#use DBI;

###########
## Globals
###########

# "Constants"
my $LOG_LEVEL_ERROR = 0;
my $LOG_LEVEL_WARNING = 1;
my $LOG_LEVEL_DEBUG1 = 2;
my $LOG_TIMESTAMP_FORMAT = '%m/%d/%Y %H:%M:%S';

# Options
my @rootDirs;
my $dbUrl = "check_files.sqlite";
my $logFile = "check_files.log";
my $fileLogLevel = $LOG_LEVEL_DEBUG1;
my $terminalLogLevel = $LOG_LEVEL_WARNING;
my $enablePruneDirs = 0;
my $disableFingerprint = 0;
my $disableDeleteCheck = 0;

# Logging stuff
my $logFH;
my $logTimeStampFormatter;

# Database stuff
my $dbh;

########
## Subs
########

# Subroutine to process the command-line arguments.
sub processArgs {

    my $showHelp = 0;
    my $quietMode = 0;
    my $verboseMode = 0;

    GetOptions("help" => \$showHelp,
	       "db=s" => \$dbUrl,
	       "prune" => \$enablePruneDirs,
	       "nofingerprint" => \$disableFingerprint,
	       "nodeletecheck" => \$disableDeleteCheck,
	       "quiet" => \$quietMode,
	       "verbose" => \$verboseMode,
	       "level=s" => \$fileLogLevel,
	       "log=s" => \$logFile
	);

    # Assume remaining arguments are root directories.
    @rootDirs = @ARGV;

    # Set terminal log level
    if($verboseMode) {
	$terminalLogLevel = $LOG_LEVEL_DEBUG1;
    } elsif ($quietMode) {
	$terminalLogLevel = $LOG_LEVEL_ERROR;
    }
 
    # Make sure all necessary variables have some value. If not,
    # show help.
    if(scalar(@rootDirs) <= 0) {
	print "Please specify one or more root directories to check! \n";
	$showHelp = 1;
    }

    if(length($dbUrl) <= 0) {
	print "Please specify the path to the fingerprint database! \n";
	$showHelp = 1;
    }

    # Show help, if requested.
    if($showHelp) {
	showHelp();
    }

    1;
}

# Displays the command-line help.
sub showHelp {

    my $name = $0;
    if(0 < rindex($name, "/")) {
	$name = substr($name, rindex($name, "/")+1);
    }
    print "Usage: $name [options] [root dirs]\n\n";

### TO DO    
    print "To Do!\n";

    exit(0);
}

# Initializes the logger
sub startLog {
    
    # Attempt to open log file for appending
    if(0 < length($logFile)) {
	logMessage("Opening log file '$logFile'...", $LOG_LEVEL_DEBUG1);
	if(open($logFH, ">>$logFile")) {
	    logMessage("File logging successfully started.", 
		       $LOG_LEVEL_DEBUG1);
	} else {
	    logMessage("Unable to log to file '$logFile'! Aborting...", 
		       $LOG_LEVEL_ERROR);
	}
    }

    1;
}

# Stops the logger
sub stopLog {

    # Indicate that we're closing the session
    logMessage("Terminating logging session.", $LOG_LEVEL_DEBUG1);

    # Close log file, if appropriate
    if(defined($logFH)) {
	close($logFH);
    }
    
    1;
}

# Logs the specified message
sub logMessage {
    my $msg = shift;
    my $level = shift;

    # Generate message
    my $logMessage = "[".DateTime->now()->strftime($LOG_TIMESTAMP_FORMAT).
	"] $msg\n";

    # Log to terminal
    if($level <= $terminalLogLevel) {
	print $logMessage;
    }

    # Log to file
    if($level <= $fileLogLevel && defined($logFH)) {
	print $logFH $logMessage;
    }

    1;
}

########
## Main
########

# Process command-line arguments
processArgs();

# Open log file
startLog();

# Open database
#openDB();

# Crawl roots
for my $root (@rootDirs) {
    logMessage("Checking $root...", $LOG_LEVEL_DEBUG1);
}

# Close database
#closeDB();

# Close log file
stopLog();

# Fini!
