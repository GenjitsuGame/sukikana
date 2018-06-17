import boto3
import configparser

def get_aws_config():
    config = configparser.ConfigParser()
    config.read('../../config.ini')
    return config['AWS']

def get_session():
    config = get_aws_config()
    return boto3.session.Session(
        aws_access_key_id=config['access_key'],
        aws_secret_access_key=config['secret_key'],
        region_name=config['region']
    )
