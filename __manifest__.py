{
    'name': 'Sale Order Payment Button',
    'version': '16.0.1.0.0',
    'summary': 'Adds payment smart button to sales orders and invoices',
    'description': """
        This module adds a payment smart button to sales orders and invoices, 
        allowing users to track payments directly from the sales order and invoice forms.
    """,
    'category': 'Sales',
    'author': '',
    'website': '',
    'depends': [
        'base',
        'sale_management',
        'sale',
        'account',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_search_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}