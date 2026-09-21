from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanYearEndClosing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Empresa Cierre CU Test",
                "country_id": cls.env.ref("base.cu").id,
                "currency_id": cls.env.ref("base.CUP").id,
            }
        )
        cls.env["account.chart.template"].try_loading("cu_494_public", cls.company)
        accounts = (
            cls.env["account.account"]
            .with_company(cls.company)
            .search([("company_ids", "in", cls.company.ids)])
        )
        cls.by_code = {account.code: account for account in accounts}
        cls.journal = (
            cls.env["account.journal"]
            .with_company(cls.company)
            .search(
                [("company_id", "=", cls.company.id), ("type", "=", "general")],
                limit=1,
            )
        )

    def _post(self, debit_code, credit_code, amount):
        move = self.env["account.move"].with_company(self.company).create(
            {
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "date": "2026-06-15",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "prueba",
                            "account_id": self.by_code[debit_code].id,
                            "debit": amount,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "prueba",
                            "account_id": self.by_code[credit_code].id,
                            "credit": amount,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        return move

    def _wizard(self, **values):
        defaults = {
            "company_id": self.company.id,
            "date_to": "2026-12-31",
            "journal_id": self.journal.id,
            "post_move": True,
            "lock_period": True,
        }
        defaults.update(values)
        return self.env["l10n_cu_closing_wizard"].create(defaults)

    def _balance(self, code):
        lines = self.env["account.move.line"].search(
            [
                ("company_id", "=", self.company.id),
                ("parent_state", "=", "posted"),
                ("account_id", "=", self.by_code[code].id),
            ]
        )
        return sum(lines.mapped("balance"))

    def test_closing_moves_nominals_to_999(self):
        self._post("135.0020", "900", 1000.0)
        self._post("810", "101", 400.0)
        wizard = self._wizard()
        wizard.action_generate()
        self.assertEqual(wizard.move_id.state, "posted")
        self.assertAlmostEqual(self._balance("900"), 0.0)
        self.assertAlmostEqual(self._balance("810"), 0.0)
        # Odoo usa balance = debe - haber: la utilidad de 600 queda como
        # saldo acreedor (-600) en 999 Resultado.
        self.assertAlmostEqual(self._balance("999"), -600.0)
        self.assertEqual(
            self.company.fiscalyear_lock_date.strftime("%Y-%m-%d"), "2026-12-31"
        )

    def test_closing_without_balances_fails(self):
        wizard = self._wizard()
        with self.assertRaises(UserError):
            wizard.action_generate()

    def test_closing_draft_and_unlocked(self):
        self._post("135.0020", "900", 500.0)
        wizard = self._wizard(post_move=False, lock_period=False)
        wizard.action_generate()
        self.assertEqual(wizard.move_id.state, "draft")
        self.assertFalse(self.company.fiscalyear_lock_date)
