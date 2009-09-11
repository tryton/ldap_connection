#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name': 'LDAP Connection',
    'version': '1.3.0',
    'author': 'B2CK, Josh Dukes & Udo Spallek',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': '''Add basic support for LDAP connection.''',
    'depends': [
        'ir',
        'res',
    ],
    'xml': [
        'connection.xml',
    ],
    'translation': [
    ],
}
