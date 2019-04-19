import os, getpass
from termcolor import colored

warningStr = colored("Make sure the bot account name matches the botName passed to 'SpazUtils.FlairRemoval'", 'yellow')
botname = input(f"What is the bot account name that you will be using? {warningStr}: ").lower()
errorStr = colored('Error:', 'red')

while not botname:
    print(f"{errorStr} Bot account name required.")
    botname = input(f"What is the bot account name that you will be using? {warningStr}: ").lower()

databaseName = input('What is the database name? [postgres]: ') or 'postgres'
dbUsername = input(f"What is the name of the database superuser (Needed to generate table and user for '{botname}')? [postgres]: ") or 'postgres'
noteStr = colored(f"If you would prefer not to enter the password for '{botname}' here, enter nothing.", 'cyan')
print(f"We need to create a password for '{botname}' to log in to '{databaseName}'.\n{noteStr}\n")

matched = False
counter = 0
limit = 3
while not matched and counter < limit:
    dbUserPassword = getpass.getpass(f"Please enter a password to use for '{botname}' or enter nothing to skip: ")
    if not dbUserPassword:
        print('Skipping password entry')
        break
    passwordConfirm = getpass.getpass(f"Please confirm password for '{botname}' or enter nothing to cancel: ")
    if passwordConfirm:
        matched = dbUserPassword == passwordConfirm
        if not matched:
            counter += 1
            if counter < limit:
                print(f'{errorStr} Passwords did not match. Please try again.')
            else:
                print(f'{errorStr} Passwords did not match. Skipping...')
    else:
        print('Canceling password entry')
        break

dbInitStr = f'''CREATE USER {botname} WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION{(f' PASSWORD "{dbUserPassword}"' if matched else '')};

CREATE SCHEMA IF NOT EXISTS {botname} AUTHORIZATION {botname};

CREATE TABLE IF NOT EXISTS {botname}.flairlog
(
    id character(36) COLLATE pg_catalog."default" NOT NULL,
    created_utc timestamp(4) with time zone,
    moderator character varying(22) COLLATE pg_catalog."default" NOT NULL,
    target_author character varying(22) COLLATE pg_catalog."default",
    target_body text COLLATE pg_catalog."default",
    target_id text COLLATE pg_catalog."default",
    target_permalink text COLLATE pg_catalog."default",
    target_title text COLLATE pg_catalog."default",
    flair text COLLATE pg_catalog."default",
    CONSTRAINT modlog_pkey PRIMARY KEY (id)
) WITH (OIDS = FALSE) TABLESPACE pg_default;

ALTER TABLE {botname}.flairlog OWNER to {botname};'''


with open('dbinit.sql', 'w') as f:
    f.write(dbInitStr)

path = (os.path.realpath('dbinit.sql'))
print('\nGenerating sql file\n')
command = colored(f'psql -d {databaseName} -U {dbUsername} -f {path}', 'green')
passwordCmd = colored(f"psql -d {databaseName}, -U {dbUsername} -c '\password {botname}'", 'green')
print(f"To finish setting up the database for '{botname}', execute:\n\n{command}\n")
if not matched:
    print(f"\nTo set the password for '{botname}' execute:\n\n{passwordCmd}\n")
command = colored(f'rm {path}', 'green')
print(f'After the database is setup, you can delete the dbinit file with:\n\n{command}\n')
