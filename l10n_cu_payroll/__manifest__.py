{
    "name": "Cuba - Nómina",
    "summary": "Nómina cubana con contabilización automática",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "author": "Comunidad cubana de Odoo",
    "website": "https://github.com/reneleonreguero/l10n-cuba-reborn",
    "license": "AGPL-3",
    "countries": ["cu"],
    "depends": ["hr", "l10n_cu_account", "l10n_cu_account_menu"],
    "data": [
        "security/ir.model.access.csv",
        "reports/report_payslip.xml",
        "views/payroll_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
