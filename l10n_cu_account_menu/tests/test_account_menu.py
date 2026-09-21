from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanAccountingMenu(TransactionCase):
    def test_accounting_app_separated_from_invoicing(self):
        root = self.env.ref("l10n_cu_account_menu.menu_cu_accounting_root")
        invoicing = self.env.ref("account.menu_finance")
        self.assertFalse(root.parent_id)
        self.assertNotEqual(root.id, invoicing.id)
        self.assertIn(
            self.env.ref("account.group_account_user"), root.group_ids
        )

    def test_accounting_actions_target_account_models(self):
        chart = self.env.ref("l10n_cu_account_menu.action_cu_chart")
        journals = self.env.ref("l10n_cu_account_menu.action_cu_journals")
        moves = self.env.ref("l10n_cu_account_menu.action_cu_moves")
        self.assertEqual(chart.res_model, "account.account")
        self.assertEqual(journals.res_model, "account.journal")
        self.assertEqual(moves.res_model, "account.move")

    def test_chart_action_lists_cuban_accounts(self):
        company = self.env["res.company"].create(
            {
                "name": "Empresa Estatal para Menú",
                "country_id": self.env.ref("base.cu").id,
                "currency_id": self.env.ref("base.CUP").id,
            }
        )
        self.env["account.chart.template"].try_loading("cu_494_public", company)
        accounts = self.env["account.account"].with_company(company).search(
            [("company_ids", "in", company.ids)]
        )
        self.assertIn("135.0020", accounts.mapped("code"))
        self.assertIn("600", accounts.mapped("code"))
