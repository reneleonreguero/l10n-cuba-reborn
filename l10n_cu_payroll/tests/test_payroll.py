from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanPayroll(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Empresa Nómina CU Test",
                "country_id": cls.env.ref("base.cu").id,
                "currency_id": cls.env.ref("base.CUP").id,
            }
        )
        cls.env["account.chart.template"].try_loading("cu_494_public", cls.company)
        cls.employee = (
            cls.env["hr.employee"]
            .with_company(cls.company)
            .create({"name": "Trabajador de prueba", "company_id": cls.company.id})
        )
        cls.contract = cls.env["l10n_cu_payroll.contract"].create(
            {
                "employee_id": cls.employee.id,
                "company_id": cls.company.id,
                "wage": 10000.0,
            }
        )
        cls.journal = (
            cls.env["account.journal"]
            .with_company(cls.company)
            .search(
                [("company_id", "=", cls.company.id), ("type", "=", "general")],
                limit=1,
            )
        )

    def _batch(self, wages=(10000.0,)):
        batch = self.env["l10n_cu_payroll.batch"].create(
            {
                "name": "Nómina 2026-09",
                "company_id": self.company.id,
                "date_from": "2026-09-01",
                "date_to": "2026-09-30",
                "journal_id": self.journal.id,
            }
        )
        for wage in wages:
            self.env["l10n_cu_payroll.slip"].create(
                {
                    "batch_id": batch.id,
                    "contract_id": self.contract.id,
                    "wage": wage,
                }
            )
        return batch

    def test_slip_computation(self):
        slip = self.env["l10n_cu_payroll.slip"].create(
            {
                "batch_id": self._batch().id,
                "contract_id": self.contract.id,
                "wage": 10000.0,
            }
        )
        self.assertEqual(slip.vacation_amount, 909.0)
        self.assertEqual(slip.ss_worker, 500.0)
        self.assertEqual(slip.ss_employer, 1250.0)
        self.assertEqual(slip.net, 9500.0)

    def test_batch_posts_balanced_move(self):
        batch = self._batch()
        batch.action_post()
        self.assertEqual(batch.state, "done")
        self.assertEqual(batch.move_id.state, "posted")
        lines = {
            line.account_id.with_company(self.company).code: (
                line.debit,
                line.credit,
            )
            for line in batch.move_id.line_ids
        }
        self.assertEqual(lines["826"], (12159.0, 0.0))
        self.assertEqual(lines["455"], (0.0, 9500.0))
        self.assertEqual(lines["460"], (0.0, 500.0))
        self.assertEqual(lines["440.0008"], (0.0, 1250.0))
        self.assertEqual(lines["492"], (0.0, 909.0))
        self.assertEqual(batch.move_id.amount_total, 12159.0)

    def test_empty_batch_fails(self):
        batch = self.env["l10n_cu_payroll.batch"].create(
            {
                "name": "Nómina vacía",
                "company_id": self.company.id,
                "date_from": "2026-09-01",
                "date_to": "2026-09-30",
                "journal_id": self.journal.id,
            }
        )
        with self.assertRaises(UserError):
            batch.action_post()

    def test_payslip_report_renders(self):
        slip = self.env["l10n_cu_payroll.slip"].create(
            {
                "batch_id": self._batch().id,
                "contract_id": self.contract.id,
                "wage": 10000.0,
            }
        )
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("l10n_cu_payroll.report_payslip", slip.ids)[0]
            .decode()
        )
        self.assertIn("Trabajador de prueba", html)
        self.assertIn("Neto a pagar", html)
