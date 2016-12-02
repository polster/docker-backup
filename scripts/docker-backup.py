#!/usr/bin/python

import os
import sys
import getopt
import subprocess
import yaml
import logging
import logging.config
import time
from docker import Client
from docker.errors import APIError

logging_config = os.getenv("LOG_CFG", "scripts/logging-config.yml")
with open(logging_config, 'rt') as f:
    config = yaml.safe_load(f.read())
logging.config.dictConfig(config)
logger = logging.getLogger('dockerBackup')

def backup_from_docker_volume( docker_cli, backup ):

    backup_date = time.strftime("%Y%m%d-%H%M%S")
    backup_command = "tar cvf /backup/" + backup['backup_file_name'] + "-" + backup_date + ".tar " + backup['backup_source_path']
    volume_container = backup['volume_container']
    volume = backup['backup_target_path'] + ":/backup"

    logger.info("Starting backup of volume container: [%s]", volume_container)

    host_config = docker_cli.create_host_config(binds=[volume], volumes_from=[volume_container])
    container = docker_cli.create_container(image="centos", command=backup_command, host_config=host_config)
    docker_cli.start(container=container.get("Id"))
    docker_cli.wait(container=container.get("Id"))
    docker_cli.remove_container(container=container.get("Id"))

def stop_docker_containers(docker_cli, docker_containers):
    for docker_container in docker_containers:
        logger.info("Stopping docker container: [%s]", docker_container)
        docker_cli.stop(docker_container)

def start_docker_containers(docker_cli, docker_containers):
    for docker_container in docker_containers:
        logger.info("Starting docker container: [%s]", docker_container)
        docker_cli.start(docker_container)

def load_config(config_file):

    with open(config_file, 'r') as yaml_file:
        yaml_config = yaml.load(yaml_file)
    return yaml_config

def usage():
    print(os.path.basename(__file__) + ' -c <config file>')

def main(argv):

    docker_cli = Client(base_url='unix://var/run/docker.sock')
    config_file = ''

    logger.info("Docker backup started")

    try:
        opts, args = getopt.getopt(argv,"hc:",["help=", "conf="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if not opts:
        print("No opts specified, check help [-h]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--conf"):
            config_file = arg

    try:
        config = load_config(config_file)
        for backup in config['backups']:
            stop_docker_containers(docker_cli, backup['docker_containers_to_stop'])
            backup_from_docker_volume(docker_cli, backup)
            start_docker_containers(docker_cli, backup['docker_containers_to_stop'])
    except APIError as docker_api_error:
        logger.error("Unexpected Docker API error: " + docker_api_error.__str__())
        sys.exit(1)
    except:
        logger.error("Unexpected error during backup: ", sys.exc_info()[0])
        sys.exit(1)

    logger.info("Docker backup completed")

if __name__ == '__main__':
    main(sys.argv[1:])
