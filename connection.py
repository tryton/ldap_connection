#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.wizard import Wizard
import ldap


class Connection(ModelSingleton, ModelSQL, ModelView):
    "LDAP Connection"
    _description = __doc__
    _name = 'ldap.connection'
    _rec_name = 'server'

    server = fields.Char('Server', required=True, help='LDAP server name')
    port = fields.Integer('Port', required=True, help='LDAP server port')
    secure = fields.Selection([
        ('never', 'Never'),
        ('ssl', 'SSL'),
        ('tls', 'TLS'),
        ], 'Secure', on_change=['secure'], required=True,
        help='LDAP secure connection')
    bind_dn = fields.Char('Bind DN', help='LDAP DN used to bind')
    bind_pass = fields.Char('Bind Pass', states={
        'required': "bool(bind_dn)",
        'readonly': "not bool(bind_dn)",
        }, help='LDAP password used to bind')
    uri = fields.Function('get_uri', type='char', string='URI')

    def default_port(self, cursor, user, context=None):
        return 389

    def default_secure(self, cursor, user, context=None):
        return 'never'

    def on_change_secure(self, cursor, user, ids, values, context=None):
        res = {}
        if values.get('secure') in ('never', 'tls'):
            res['port'] = self.default_port(cursor, user, context=context)
        elif values.get('secure') == 'ssl':
            res['port'] = 636
        return res

    def get_uri(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for connection in self.browse(cursor, user, ids, context=context):
            res[connection.id] = \
                    (connection.secure == 'ssl' and 'ldaps' or 'ldap') + \
                    '://%s:%s/' % (connection.server, connection.port)
        return res

    def write(self, cursor, user, ids, values, context=None):
        if 'bind_dn' in values and not values['bind_dn']:
            values = values.copy()
            values['bind_pass'] = False
        return super(Connection, self).write(cursor, user, ids, values,
                context=context)

Connection()


class TestConnectionInit(ModelView):
    'Test Connection - Init'
    _description = __doc__
    _name = 'ldap.test_connection.init'

TestConnectionInit()


class TestConnection(Wizard):
    "Test LDAP Connection"
    _description = __doc__
    _name = 'ldap.test_connection'
    states = {
        'init': {
            'actions': ['_test'],
            'result': {
                'type': 'form',
                'object': 'ldap.test_connection.init',
                'state': [
                    ('end', 'Ok', 'tryton-ok', True),
                ],
            },
        },
    }

    def _test(self, cursor, user, data, context=None):
        connection_obj = self.pool.get('ldap.connection')
        connection_ids = connection_obj.search(cursor, user, [],
                limit=1, context=context)
        connection = connection_obj.browse(cursor, user, connection_ids[0],
                context=context)
        con = ldap.initialize(connection.uri)
        if connection.secure == 'tls':
            con.start_tls_s()
        if connection.bind_dn:
            con.simple_bind_s(connection.bind_dn, connection.bind_pass)
        else:
            con.simple_bind_s()
        return {}

TestConnection()
