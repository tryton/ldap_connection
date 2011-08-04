#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import ldap
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.wizard import Wizard
from trytond.pyson import Bool, Not, Eval
from trytond.pool import Pool


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
            'required': Bool(Eval('bind_dn')),
            'readonly': Not(Bool(Eval('bind_dn'))),
            }, help='LDAP password used to bind',
        depends=['bind_dn'])
    uri = fields.Function(fields.Char('URI'), 'get_uri')
    active_directory = fields.Boolean('Active Directory')

    def default_port(self):
        return 389

    def default_secure(self):
        return 'never'

    def default_active_directory(self):
        return False

    def on_change_secure(self, values):
        res = {}
        if values.get('secure') in ('never', 'tls'):
            res['port'] = self.default_port()
        elif values.get('secure') == 'ssl':
            res['port'] = 636
        return res

    def get_uri(self, ids, name):
        res = {}
        for connection in self.browse(ids):
            res[connection.id] = \
                    (connection.secure == 'ssl' and 'ldaps' or 'ldap') + \
                    '://%s:%s/' % (connection.server, connection.port)
        return res

    def write(self, ids, values):
        if 'bind_dn' in values and not values['bind_dn']:
            values = values.copy()
            values['bind_pass'] = False
        return super(Connection, self).write(ids, values)

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

    def _test(self, data):
        connection_obj = Pool().get('ldap.connection')
        connection_ids = connection_obj.search([],
                limit=1)
        connection = connection_obj.browse(connection_ids[0])
        con = ldap.initialize(connection.uri)
        if connection.secure == 'tls':
            con.start_tls_s()
        if connection.bind_dn:
            con.simple_bind_s(connection.bind_dn, connection.bind_pass)
        else:
            con.simple_bind_s()
        return {}

TestConnection()
