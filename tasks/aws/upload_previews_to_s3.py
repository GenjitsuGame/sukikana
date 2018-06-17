import boto3
import boto_utils
import configparser
import sys
import os

config = configparser.ConfigParser()
config.read('../../config.ini')
aws_config = config['AWS']

session = boto_utils.get_session()

s3 = session.client('s3')

input_dir = sys.argv[1]

for file in os.listdir(input_dir):
    filepath = os.path.join(input_dir, file)
    s3.upload_file('')
