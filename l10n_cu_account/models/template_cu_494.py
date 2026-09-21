from odoo import _, models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("cu_494_common")
    def _get_cu_494_common_template_data(self):
        return {
            "name": _("Cuba - Base empresarial (Resolucion 494/2016)"),
            "country": "base.cu",
            "visible": False,
            "code_digits": 3,
            "property_account_receivable_id": "account_135_0020",
            "property_account_payable_id": "account_405_0020",
        }

    @template("cu_494_common", "res.company")
    def _get_cu_494_common_res_company(self):
        return {
            self.env.company.id: {
                "account_fiscal_country_id": "base.cu",
                "bank_account_code_prefix": "109",
                "cash_account_code_prefix": "101",
                "transfer_account_code_prefix": "119",
                "income_currency_exchange_account_id": "account_924",
                "expense_currency_exchange_account_id": "account_839",
                "default_cash_difference_income_account_id": "account_930",
                "default_cash_difference_expense_account_id": "account_845",
                "expense_account_id": "account_810",
                "income_account_id": "account_900",
                "account_sale_tax_id": "tax_iventas_10",
                "account_purchase_tax_id": "tax_exento_0",
                "fiscalyear_last_day": 31,
                "fiscalyear_last_month": "12",
            }
        }

    @template("cu_494_public")
    def _get_cu_494_public_template_data(self):
        return {
            "name": _("Cuba - Empresa estatal (Resolucion 494/2016)"),
            "country": "base.cu",
            "parent": "cu_494_common",
            "sequence": 1,
        }

    @template("cu_494_private")
    def _get_cu_494_private_template_data(self):
        return {
            "name": _("Cuba - Mipyme y cooperativa (Resolucion 494/2016)"),
            "country": "base.cu",
            "parent": "cu_494_common",
            "sequence": 2,
        }
