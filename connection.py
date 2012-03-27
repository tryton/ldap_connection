#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import ldap
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Bool, Eval
from trytond.pool import Pool
from trytond.transaction import Transaction


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
            'readonly': ~Eval('bind_dn'),
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
            values['bind_pass'] = None
        return super(Connection, self).write(ids, values)

Connection()


class TestConnectionResult(ModelView):
    'Test Connection'
    _description = __doc__
    _name = 'ldap.test_connection.result'

TestConnectionResult()


class TestConnection(Wizard):
    "Test LDAP Connection"
    _description = __doc__
    _name = 'ldap.test_connection'
    start_state = 'test'

    test = StateTransition()
    result = StateView('ldap.test_connection.result',
        'ldap_connection.test_connection_result_form', [
            Button('Close', 'end', 'tryton-close'),
            ])

    def transition_test(self, session):
        connection_obj = Pool().get('ldap.connection')
        connection_id = Transaction().context.get('active_id')
        connection = connection_obj.browse(connection_id)
        con = ldap.initialize(connection.uri)
        if connection.secure == 'tls':
            con.start_tls_s()
        if connection.bind_dn:
            con.simple_bind_s(connection.bind_dn, connection.bind_pass)
        else:
            con.simple_bind_s()
        return 'result'

TestConnection()
