from repoze.who.config import make_middleware_with_config
from elixir import metadata
from config import config

from repoze.who.middleware import PluggableAuthenticationMiddleware
from repoze.who.interfaces import IIdentifier
from repoze.who.interfaces import IChallenger
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
#from repoze.who.plugins.form import FormPlugin
from repoze.who.plugins.htpasswd import HTPasswdPlugin
from repoze.who.plugins.sql import make_authenticator_plugin
from repoze.who.plugins.sql import default_password_compare
from repoze.who.plugins.sql import SQLAuthenticatorPlugin
from repoze.who.classifiers import default_request_classifier
from repoze.who.classifiers import default_challenge_decider

def setup_auth(app):

    basicauth = BasicAuthPlugin('repoze.who')
    auth_tkt = AuthTktCookiePlugin('secret', 'auth_tkt')
    #form = FormPlugin('__do_login', rememberer_name='auth_tkt')
    #form.classifications = { IIdentifier:['browser'],
    #                         IChallenger:['browser'] } # only for browser
    query = "SELECT id, password_hash FROM users where handle = ?;"
    conn_factory = metadata.bind.raw_connection().cursor
    compare = default_password_compare
    sqlauth = SQLAuthenticatorPlugin(query,conn_factory,compare)

    identifiers = [#('form',form),
                   ('auth_tk',auth_tkt),
                   ('basicauth',basicauth)]

    authenticators = [#('sqlauth',sqlauth),
                      ('auth_tkt', auth_tkt)]

    challengers = [#('form', form),
                   ('basicauth',basicauth)]

    mdproviders = []

    middlewear = PluggableAuthenticationMiddleware(
        app,
        identifiers,
        authenticators,
        challengers,
        mdproviders,
        default_request_classifier,
        default_challenge_decider
    )
    print 'returning middleware'
    return middlewear


def conn_factory():
    return metadata.bind.raw_connection().cursor
