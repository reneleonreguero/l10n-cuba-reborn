{
    "name": "Cuba - Contabilidad (menús)",
    "summary": "Aplicación Contabilidad separada de Facturación para Cuba",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations/Account Charts",
    "author": "Comunidad cubana de Odoo",
    "website": "https://github.com/reneleonreguero/l10n-cuba-reborn",
    "license": "AGPL-3",
    "countries": ["cu"],
    "depends": ["l10n_cu_account", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_menu.xml",
        "views/closing_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
