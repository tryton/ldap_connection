#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'LDAP Connection',
    'name_de_DE' : 'LDAP Verbindung',
    'version': '1.3.0',
    'author': 'B2CK, Josh Dukes & Udo Spallek',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': '''Add basic support for LDAP connection.''',
    'description_de_DE' : '''LDAP Verbindung
    - Fügt Basisunterstützung für Verbindungen zu einem LDAP-Server hinzu
''',
    'depends': [
        'ir',
        'res',
    ],
    'xml': [
        'connection.xml',
    ],
    'translation': [
        'de_DE.csv',
    ],
}
