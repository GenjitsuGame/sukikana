import boto3
import configparser
import os

def get_aws_config():
    config = configparser.ConfigParser()
    config.read(os.environ['CONFIG'])
    return config['AWS']

def get_session():
    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG')
    if config_path is not None:
        config.read(config_path)

    return boto3.session.Session(
        aws_access_key_id=os.environ.get('SUKIKANA_AWS_ACCESS', config['AWS']['access_key']),
        aws_secret_access_key=os.environ.get('SUKIKANA_AWS_SECRET_KEY', config['AWS']['secret_key']),
        region_name=os.environ.get('SUKIKANA_AWS_REGION', config['AWS']['region'])
    )
