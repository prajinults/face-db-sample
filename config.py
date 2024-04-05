import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """ base config """
    DEBUG = False
    TESTING = False
    OIDC_RESOURCE_SERVER_ONLY = True
    OIDC_OPENID_REALM=os.environ['OIDC_OPENID_REALM']
    OIDC_SCOPES = ['openid', 'email', 'profile']
    OIDC_CLIENT_SECRETS= os.environ['OIDC_CLIENT_SECRETS'] 
    OIDC_INTROSPECTION_AUTH_METHOD='client_secret_post'
    OIDC_TOKEN_TYPE_HINT='access_token'


class ProductionConfig(Config):
    """Producttion config"""
    DEBUG = False

class DevelopmentConfig(Config):
    """Development config"""
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    """testing config"""
    TESTING = True