from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanChartTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cuba = cls.env.ref("base.cu")
        cls.cup = cls.env.ref("base.CUP")

    def _new_company(self, name, template):
        company = self.env["res.company"].create(
            {
                "name": name,
                "country_id": self.cuba.id,
                "currency_id": self.cup.id,
            }
        )
        self.env["account.chart.template"].try_loading(template, company)
        return company

    def _accounts(self, company):
        return self.env["account.account"].with_company(company).search(
            [("company_ids", "in", company.ids)]
        )

    def test_public_chart(self):
        company = self._new_company("Empresa Estatal CU Test", "cu_494_public")
        accounts = self._accounts(company)
        by_code = {account.code: account for account in accounts}

        self.assertEqual(company.chart_template, "cu_494_public")
        self.assertIn("101", by_code)
        self.assertNotIn("102", by_code)
        self.assertEqual(by_code["109"].account_type, "asset_cash")
        self.assertEqual(by_code["135.0020"].account_type, "asset_receivable")
        self.assertEqual(by_code["405.0020"].account_type, "liability_payable")
        self.assertEqual(by_code["999"].account_type, "equity_unaffected")
        self.assertIn("Inversión Estatal", by_code["600"].name)
        self.assertEqual(len(accounts.mapped("code")), len(set(accounts.mapped("code"))))

    def test_private_chart(self):
        company = self._new_company("Mipyme CU Test", "cu_494_private")
        accounts = self._accounts(company)
        by_code = {account.code: account for account in accounts}

        self.assertEqual(company.chart_template, "cu_494_private")
        self.assertIn("Patrimonio y Fondo Común", by_code["600"].name)
        self.assertNotIn("Devoluciones de Primas", accounts.mapped("name"))

    def test_public_chart_posts_balanced_entry(self):
        company = self._new_company("Empresa Asientos CU Test", "cu_494_public")
        accounts = self._accounts(company)
        cash = accounts.filtered(lambda account: account.code == "101")
        equity = accounts.filtered(lambda account: account.code == "600")
        journal = self.env["account.journal"].with_company(company).search(
            [("company_id", "=", company.id), ("type", "=", "general")], limit=1
        )
        move = self.env["account.move"].with_company(company).create(
            {
                "company_id": company.id,
                "journal_id": journal.id,
                "date": "2026-01-01",
                "line_ids": [
                    (0, 0, {"name": "Apertura", "account_id": cash.id, "debit": 100.0}),
                    (0, 0, {"name": "Apertura", "account_id": equity.id, "credit": 100.0}),
                ],
            }
        )
        move.action_post()
        self.assertEqual(move.state, "posted")
