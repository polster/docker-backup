Docker Backup Script
====================

## Product box description

* Quick and dirty Python script used to backup a volume container's data
* Configure one or more locations per volume container to be included into the backup (yaml config)
* Let I/O sensitive docker containers depending on the volume content be stopped before backup and restarted after completion

## Disclaimer

Use this script at your own risk as the script may cause downtimes or any other unexpected changes to your Docker environment in case of misconfiguration or bugs!

## Prerequisites

* Python 2.7
* [docker-py](https://docker-py.readthedocs.io/en/stable/)
* Docker 1.12.3

## Ops Manual

### Print script usage

```
python docker-backup.py --help
```

### Backup configuration

* The backup configuration needs to be declared maintaining the following structure (sample yml):
```
backups:
  -
    volume_container: "repodata"
    backup_target_path: "/docker-backup"
    backup_source_path: "/usr/local/apache2/htdocs/repo"
    backup_file_name: "backup-repodata"
    docker_containers_to_stop:
      - "repo"
```

| Param | Description |
|-------|-------------|
| volume_container | The docker volume container used to mount its volumes for backup |
| backup_target_path | The target backup path located on the docker host |
| backup_source_path | The path to be files to be backed-up |
| backup_file_name | The backup file name, where the script will append the current time stamp and correct file type |
| docker_containers_to_stop | One or more container to be stopped before backup and restart after completion |

* Once the backup configuration has been defined, it needs to be passed in as script parameter. Print help for more details:
```
python docker-backup.py --help
```

### Logging

* This script allows to specify and load a custom logging configuration (yaml)
* As a reference, see [logging-config](scripts/logging-config.yml)
* Export the following variable pointing to your logging config where the script will automatically read the variable and try to load the config:
```
LOG_CFG="/path/to/logging-config.yml"
```

## Dev Manual

### Local setup

* Git clone this project
* cd into <project root>/devenv
* Setup the pre-configured Docker environment:
```
make docker-run
```
* cd into the <project root>
* Run the following command in order to see if the script runs through and creates a backup:
```
python scripts/docker-backup.py --conf scripts/docker-backup-config.yml
```
* By default, some log messages should be printed and a backup file will be created as well containing the <project root>/devenv/repodata content

## Known issues

* Although this script already uses the Docker API, it still has to be executed on the docker host itself
