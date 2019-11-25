{
    'name': 'Manufacturing Reports in Excel',
    'author': 'Itech resources',
    'company': 'ItechResources',
    'depends': [
                'base',
                'stock',
                'sale',
                'purchase',
                'report_xlsx'
                ],
    'data': [
            'views/wizard_view.xml',
            'views/bom_sum.xml',

            ],
    'installable': True,
    'price':'15.0',
    'currency': 'EUR',
    'auto_install': False,
}
