#!/usr/bin/perl

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
use DateTime::Format::SQLite;
use File::stat;
use DBI;

###########
## Globals
###########

# "Constants"
my $LOG_LEVEL_ERROR = 0;
my $LOG_LEVEL_WARNING = $LOG_LEVEL_ERROR + 1;
my $LOG_LEVEL_INFO = $LOG_LEVEL_WARNING + 1;
my $LOG_LEVEL_DEBUG1 = $LOG_LEVEL_INFO + 1;
my $LOG_TIMESTAMP_FORMAT = '%m/%d/%Y %H:%M:%S';

# Options
my @rootDirs;
my $dbUrl = "check_files.sqlite";
my $tableName = "Fingerprints";
my $logFile = "check_files.log";
my $fileLogLevel = $LOG_LEVEL_DEBUG1;
my $terminalLogLevel = $LOG_LEVEL_WARNING;
my $enablePruneDirs = 0;
my $disableFingerprint = 0;
my $disableDeleteCheck = 0;
my $fingerPrinter = '/usr/bin/sha1sum'

# Logging stuff
my $logFH;
my $logTimeStampFormatter;

# Database stuff
my $dbh;

# Crawler stuff
my $filesGood = 0;
my $filesBad = 0;
my $filesDeleted = 0;
my $filesAdded = 0;
my $filesUpdated = 0;
my $totalFiles = 0;

########
## Subs
########

## Command-line Subs ##

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
	$terminalLogLevel = $LOG_LEVEL_INFO;
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

## Logger Subs ##

# Initializes the logger
sub startLog {
    
    # Attempt to open log file for appending
    if(0 < length($logFile)) {
	logMessage("Opening log file '$logFile'...", $LOG_LEVEL_INFO);
	if(open($logFH, ">>$logFile")) {
	    logMessage("File logging successfully started.", 
		       $LOG_LEVEL_INFO);
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
    logMessage("Terminating logging session.", $LOG_LEVEL_INFO);

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

    my $type = "";

    # Check inputs
    if(!defined($level)) {
	$level = $LOG_LEVEL_ERROR;
    }
    if(!defined($msg)) {
	$level = $LOG_LEVEL_ERROR;
	$msg = "Log called w/ unspecified message.";
    }

    # Generate message
    if($level == $LOG_LEVEL_ERROR) {
	$type = " <<< ERROR >>>";
    } elsif($level == $LOG_LEVEL_WARNING) {
	$type = " << Warning >>";
    } elsif($level == $LOG_LEVEL_INFO) {
	$type = " < Info >";
    } else {
	$type = " < Debug >";
    }
    my $logMessage = "[".DateTime->now()->strftime($LOG_TIMESTAMP_FORMAT).
	"]$type $msg\n";

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

## Database Subs ##

# Opens the database. If the specified URL doesn't exist, it is created.
# The database fingerprint is generated and checked prior to opening.
sub openDB {

    my $dbResult;

    # Attempt to open database
    $dbh = DBI->connect("dbi:SQLite:dbname=$dbUrl", "", "", 
			{ RaiseError => 1} );
    if($dbh == 0) {
	logMessage("Unable to open database '$dbUrl': ".$DBI::errstr, 
		   $LOG_LEVEL_ERROR);
	exit(1);
    }

    # Grab a list of database tables
    my @tables = $dbh->tables();
    my $tableFound = 0;
    for my $tmpTable (@tables) {
	my $table = $tmpTable;
	if($table =~ /\."(.*)\"/) {
	    $table = $1;
	}
	logMessage("Found table '$tmpTable' -> '$table'...", 
		   $LOG_LEVEL_DEBUG1);
	if($table eq $tableName) {
	    $tableFound = 1;
	    logMessage("Fingerprints table '$table' found.", $LOG_LEVEL_INFO);
	}
    }

    # Create table, if necessary
    if(!$tableFound) {
	logMessage("Unable to find fingerprints table '$tableName'. Creating...", 
		   $LOG_LEVEL_WARNING);
	$dbResult = $dbh->do("CREATE TABLE '$tableName'(id INT PRIMARY KEY, ".
			     "Path TEXT, LastModified TEXT, ".
			     "Fingerprint TEXT, Size INT)");
	if(!defined($dbResult)) {
	    logMessage("Unable to create table '$tableName': ".$dbh->errstr,
		       $LOG_LEVEL_ERROR);
	    exit(1);
	}

    }

    1;
}

# Closes the database, committing any outstanding transactions. Additionally,
# updates the fingerprint after closing.
sub closeDB {

    logMessage("Closing database...", $LOG_LEVEL_INFO);
#    $dbh->commit or logMessage("Error committing: ".$dbh->errstr, 
#			       $LOG_LEVEL_ERROR);
    $dbh->disconnect() or 
	logMessage("Problem disconnecting database: ".$dbh->errstr,
		   $LOG_LEVEL_WARNING);
    1;
}

# Retrieves the list of all files in the given directory from the
# database and returns a reference to a "checklist" or a hash of filenames
# as keys with values of 0.
sub getDirListFromDB {
    my $target = shift;
    my %retVal;

    if(!defined($target)) {
	logMessage("Invalid target specified to getDirListFromDB", 
		   $LOG_LEVEL_ERROR);
	return 0;
    }

    my $sth = $dbh->prepare( "SELECT 'Path' FROM '$tableName' WHERE 'Path' ".
			     "LIKE ?" );

    if(!$sth->execute("$target/[%/]")) {
	logMessage("Unable to retrieve database listing for '$target': ".
		   $dbh->errstr, $LOG_LEVEL_INFO);
    } else {
	# Add to checklist
	my @row;
	while(@row = $sth->fetchrow_array()) {
	    $retVal{$row[0]} = 0;
	}
    }

    # return checklist
    return \%retVal;
}

## Directory Crawler Subs ##

# Recursively crawls the specified target if it's a directory. If target is
# a file, this routine passes it on to the file processor.
sub crawlPath {
    my $target = shift;

    if(!defined($target)) {
	logMessage("Invalid argument to crawlPath!", $LOG_LEVEL_ERROR);
	return 0;
    }

    if(-d $target) {
	logMessage("Processing directory '$target'...", $LOG_LEVEL_DEBUG1);

	# Attempt to open directory
	if(!opendir(TMPDIR, "$target")) {
	    logMessage("Unable to open directory '$target' for reading $!", 
		       $LOG_LEVEL_ERROR);
	    return 0;
	}

	# Grab contents of this directory from database so that we can check
	# them off as we go.
	my $haveSeenRef;
	if(!$disableDeleteCheck) {
	    $haveSeenRef = getDirListFromDB($target);
	}

	# Iterate over contents
	while(readdir(TMPDIR)) {
	    my $newTarget = $_;

	    # Ignore . and ..
	    if($newTarget ne "." && $newTarget ne "..") {
		# Check the new target's type. If it's a file, pass it on to
		# file processor. Otherwise crawl it.
		if(-f $newTarget) {
		    # Mark this item off in the "have seen" checklist
		    if(!$disableDeleteCheck) {
			$haveSeenRef->{$newTarget} = 1;
		    }
		    processFile("$target/$newTarget");
		} else {
		    crawlPath("$target/$newTarget");
		}
	    }
	}

	# Close directory
	closedir(TMPDIR);

	# Iterate over the "have seen" list and handle any objects that haven't
	# been seen.
	if(!$disableDeleteCheck) {
	    my @deletedFiles = grep {!$haveSeenRef->{$_}} keys(%{$haveSeenRef});
	    @deletedFiles = map {"$target/$_"} @deletedFiles;
	    handleMissingFiles(\@deletedFiles);
	}

    } elsif( -f $target) {
	processFile($target);
    } else {
	logMessage("Don't know how to handle object '$target'. Skipping...", 
		   $LOG_LEVEL_WARNING);
    }

    1;
}

# Processes the specified file.
sub processFile {
    my $target = shift;

    my $failFingerprint = 0;
    my $newerDate = 0;

    if(!defined($target)) {
	logMessage("Invalid argument to processFile!", $LOG_LEVEL_ERROR);
	return 0;
    }
    
    logMessage("Processing file '$target'...", $LOG_LEVEL_DEBUG1);

    # Grab file attributes
    my $fileAttrsRef = stat($target);
    my $fingerPrint = "";
    my $modTime;
    if(!defined($fileAttrsRef)) {
	logMessage("Unable to stat file '$target'!", $LOG_LEVEL_ERROR);
	return 0;
    }

    $totalFiles += 1;

    # Find file in database
    my $entryData;
    my $sth = $dbh->prepare( "SELECT * FROM '$tableName' WHERE 'Path'=?");

    # Generate fingerprint of file
    if(!$disableFingerprint) {
	$fingerPrint = `$fingerPrinter $target`;
	# Strip out space and filename
	my $spaceLoc = index($fingerPrint, " ");
	if(0 <= $spaceLoc) {
	    $fingerPrint = substr($fingerPrint, 0, $spaceLoc);
	}
	
	# Log calculated fingerprint for debugging
	logMessage("File '$target' has fingerprint '$fingerPrint'", 
		   $LOG_LEVEL_DEBUG1);
    }

    if($sth->execute($target)) {
	# Grab first entry and stuff it into @entryData
	$entryData = $sth->fetchrow_hashref();
	logMessage("File '$target' found in database with ID number '".
		   $entryData{"id"}, $LOG_LEVEL_DEBUG1);

	## Check file against database ##
	
	# Check mod time
	my $dbModTime = DateTime::Format::SQLite->parse_datetime(
	    $entryData->{"LastModified"});
	my $fileModTime = DateTime->from_epoch(epoch=>$ref->[9]);
	if(DateTime->compare($dbModTime, $fileModTime) < 0) {
	    logMessage("Database entry for file '$target' is out of date.", 
		       $LOG_LEVEL_INFO);
	    $newerDate = 1;
	}
	
	if(!$disableFingerprint) {
	    if($fingerPrint ne $entryData->{"Fingerprint"}) {
		if($newerDate) {
		    logMessage("File '$target' fingerprint doesn't match ".
			       "database.", $LOG_LEVEL_INFO);
		} else {
		    logMessage("File '$target' fingerprint doesn't match ".
			       "database. File may have been damaged!",
			       $LOG_LEVEL_ERROR);
		    $filesBad += 1;
		}
		$failFingerprint = 1;
	    } else {
		$filesGood += 1;
	    }
	}

	if($newerDate) {
	    logMessage("Updating database entry for '$target' (ID=".
		       $entryData->{"id"}."...", $LOG_LEVEL_INFO);

	    $modTime = genSQLiteModTime($fileAttrsRef);
	    $sth = $dbh->prepare("UPDATE'$tableName' SET LastModified=?, ".
				 "Fingerprint=?, Size=? WHERE id=?");
	    if(!$sth->execute($modTime, $fingerPrint, $fileAttrsRef->[7],
			      $entryData->{"id"})) {
		logMessage("Error updating entry for file '$target' in table ".
			   "'$tableName': ".$dbh->errstr, $LOG_LEVEL_ERROR);
	    } else {
		logMessage("Successfully updated '$target' in database.", 
			   $LOG_LEVEL_DEBUG1);
		$filesUpdated += 1;
	    }
	}
	
    } else {
	logMessage("File '$target' not found in database. Adding...",
		   $LOG_LEVEL_INFO);
	
	$modTime = genSQLiteModTime($fileAttrsRef);
	
	$sth = $dbh->prepare("INSERT INTO '$tableName'(Path, LastModified, ".
			     "Fingerprint, Size) VALUES (?, ?, ?, ?)");
	if(!$sth->execute($target, $modTime, $fingerPrint, 
			  $fileAttrsRef->[7])) {
	    logMessage("Error inserting file '$target' into table ".
		       "'$tableName': ".$dbh->errstr, $LOG_LEVEL_ERROR);
	} else {
	    logMessage("Successfully added '$target' to database.", 
		       $LOG_LEVEL_DEBUG1);
	    $filesAdded += 1;
	}
    }



    1;
}

# Handles missing files
sub handleMissingFiles {
    my $listRef = shift;

    if(!defined($listRef)) {
	logMessage("Invalid argument passed to handleMissingFiles!", 
		   $LOG_LEVEL_ERROR);
	return 0;
    }

    for my $path (@{$listRef}) {
	if($enablePruneDirs) {
	    logMessage("File '$path' no longer exists. Deleting from ".
		       "database...", $LOG_LEVEL_INFO);

	    my $sth = $dbh->prepare("DELETE FROM '$tableName' WHERE 'Path'=?");
	    if(!$sth->execute($path)) {
		logMessage("Unable to remove file '$path' from table ".
			   "'$tableName': ".$dbh->errstr, $LOG_LEVEL_ERROR);
	    }
	} else {
	    logMessage("File '$path' no longer exists!", $LOG_LEVEL_WARNING);
	}

	$filesDeleted += 1;
    }

    1;
}

# Sub to generate a SQLite date from the output of stat()
sub genSQLiteModTime {
    my $ref = shift;

    if(!defined($ref) || scalar($ref) < 13) {
	logMessage("Invalid argument to genSQLiteModTime!", $LOG_LEVEL_ERROR);
	return "";
    }

    return DateTime::Format::SQLite->format_datetime(
	DateTime->from_epoch(epoch=>$ref->[9]));
}

########
## Main
########

# Process command-line arguments
processArgs();

# Open log file
startLog();

# Open database
openDB();

# Crawl roots
for my $root (@rootDirs) {
    logMessage("Checking '$root'...", $LOG_LEVEL_INFO);
}

# Close database
closeDB();

# Close log file
stopLog();

# Fini!
