import os

class ParamGetter():
    def __init__(self, boto_session=None, config=None, args=None, env=False):
        self.ssm = None
        if boto_session:
            self.ssm = boto_session.client('ssm', region_name='eu-west-2')
        self.config = config
        self.args = args
        self.env = env

    def get(self, key, namespace='DEFAULT', ssm=True, config=True, args=True, env=True, fallback=None):
        value = None
        if self.args and args:
            value = self.args.get(key.lower())
        if value:
            return value

        if self.config and config and namespace:
            value = self.config.get(namespace.upper(), key.lower(), fallback=None)
        if value:
            return value

        if self.env and env:
            value = os.environ.get(key.upper())
        if value:
            return value

        if self.ssm and ssm:
            try:
                value = self.ssm.get_parameter(Name=key.upper())['Parameter']['Value']
            except:
                pass
        if value:
            return value

        return fallback
