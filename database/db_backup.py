import os
import configparser
import subprocess
import time
from datetime import datetime, timedelta, date

# change dir to directory of this file so we can find the config file
os.chdir(os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.read(R'backup_config.ini')

BACKUP_DIR = config['BACKUP_DIR']['backup_dir']


def get_backup_file_list():
    '''
    Get a list of the files currently in the backup directory
    '''
    backup_files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(
        BACKUP_DIR) if os.path.isfile(os.path.join(BACKUP_DIR, f))]

    return backup_files


def delete_oldest_backups(backup_file_list):
    '''
    Simply delete the oldest file in a list of files
    '''
    for f in backup_file_list:
        file_created_time = datetime.strptime(time.ctime(
            os.path.getctime(f)), "%a %b %d %H:%M:%S %Y")

        current_date = datetime.today()
        date_cutoff = current_date - timedelta(days=7)

        if file_created_time < date_cutoff:
            os.remove(f)


def backup_db(db_location, backup_directory):
    '''
    Copy the database over to the backup directory and rename it with the backup date
    '''
    database_filename = os.path.basename(db_location)
    # Vacuum the geopackage
    subprocess.run(["ogrinfo", f"{db_location}", "-sql", "VACUUM"])

    backup_filename = '{}_{}'.format(date.today(), database_filename)

    backup_full_path = os.path.join(backup_directory, backup_filename)

    # VACUUM INTO to create backup
    subprocess.run(["ogrinfo", f"{db_location}",
                   "-sql", f"VACUUM INTO '{backup_full_path}'"])

    if os.path.isfile(backup_full_path):
        print(f'\n------{backup_filename} backup created successfully')
    else:
        print(f'\n------[{backup_filename} -- backup failed')


def main():
    databases = config.items('DATABASE_PATHS')
    for database, db_path in databases:
        backup_db(db_path, BACKUP_DIR)

    backup_file_list = get_backup_file_list()

    delete_oldest_backups(backup_file_list)


if __name__ == '__main__':
    main()
