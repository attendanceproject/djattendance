#!/bin/bash

set -e

MIGRATIONBASE=/home/ftta-ap/migrations
VENVDIR=/home/ftta-ap/.virtualenvs/backup
DATABACK=/home/ftta-ap/db_backup
SCRIPTBACK=/home/ftta-ap/script_backup

source $VENVDIR/bin/activate

lockfile="./.git/index.lock"

#Backup Database
cd $DATABACK
# take care of git lock file
if [ -f $lockfile ] ; then
    rm $lockfile
fi
pg_dump -U postgres djattendance > ap_data.sql --exclude-table=django_migrations
pg_dump -U postgres djattendance > ap_full.sql
pg_dump -U postgres -s djattendance > ap_schema.sql
git add -A
now=$(date +"%m_%d_%Y_%H%M%S")
git commit -am "Backup Database. Date: $now"
git push dropbox database

# upload to dropbox (uses dropbox uploader)
# https://github.com/andreafabrizi/Dropbox-Uploader
./dropbox_uploader.sh upload ap_data.sql /db_backups/

#Backup Scipts
cd $SCRIPTBACK
if [ -f $lockfile ] ; then
    rm $lockfile
fi
git add -A
now=$(date +"%m_%d_%Y_%H%M%S")
git commit -am "Backup scripts. Date: $now"
git push dropbox scripts
