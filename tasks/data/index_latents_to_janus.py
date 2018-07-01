import param_utils
import boto3
import configparser
import argparse
import os

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='')
    arg_parser.add_argument('-i', '--input', type=str)
    arg_parser.add_argument('-c', '--config', type=str)
    args = vars(arg_parser.parse_args())

    config = configparser.ConfigParser()
    config_path = os.environ.get('CONFIG', args.get('config'))
    if config_path is not None:
        config.read(config_path)

    boto_session = boto3.session.Session(region_name='eu-west-3')

    paramGetter = param_utils.ParamGetter(boto_session=boto_session, config=config, args=args, env=True)

    s3 = boto_session.resource('s3')
