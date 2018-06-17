import boto3
import boto_utils
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
import configparser

config = configparser.ConfigParser()
config.read('../../config.ini')
aws_config = config['AWS']

session = boto_utils.get_session()

credentials = session.get_credentials().get_frozen_credentials()

awsauth = AWSRequestsAuth(
    aws_access_key=credentials.access_key,
    aws_secret_access_key=credentials.secret_key,
    aws_token=credentials.token,
    aws_host=aws_config['es_host'],
    aws_region=session.region_name,
    aws_service='es'
)

# use the requests connection_class and pass in our custom auth class
es = Elasticsearch(
    hosts=[{'host': aws_config['es_host'], 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

print(es.info())
