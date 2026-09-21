from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Empresa Factura CU Test",
                "country_id": cls.env.ref("base.cu").id,
                "currency_id": cls.env.ref("base.CUP").id,
            }
        )
        cls.env["account.chart.template"].try_loading("cu_494_public", cls.company)
        cls.company.partner_id.vat = "12345678901"

    def _invoice(self, partner):
        return (
            self.env["account.move"]
            .with_company(self.company)
            .create(
                {
                    "company_id": self.company.id,
                    "move_type": "out_invoice",
                    "partner_id": partner.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Venta de prueba",
                                "quantity": 1,
                                "price_unit": 1000.0,
                            },
                        )
                    ],
                }
            )
        )

    def test_receptor_sin_identificador_no_publica(self):
        partner = self.env["res.partner"].create({"name": "Sin datos"})
        with self.assertRaises(ValidationError):
            self._invoice(partner).action_post()

    def test_receptor_persona_natural_con_ci_publica(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Persona natural",
                "is_company": False,
                "country_id": self.env.ref("base.cu").id,
                "l10n_cu_ci": "90010112345",
            }
        )
        invoice = self._invoice(partner)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_receptor_persona_juridica_con_nit_publica(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Empresa cliente",
                "is_company": True,
                "country_id": self.env.ref("base.cu").id,
                "vat": "98765432109",
            }
        )
        invoice = self._invoice(partner)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_emisor_sin_nit_no_publica(self):
        self.company.partner_id.vat = False
        partner = self.env["res.partner"].create(
            {
                "name": "Cliente con NIT",
                "is_company": True,
                "country_id": self.env.ref("base.cu").id,
                "vat": "98765432109",
            }
        )
        with self.assertRaises(ValidationError):
            self._invoice(partner).action_post()

    def test_reporte_muestra_nit_y_ci(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Persona natural",
                "is_company": False,
                "country_id": self.env.ref("base.cu").id,
                "l10n_cu_ci": "90010112345",
            }
        )
        invoice = self._invoice(partner)
        invoice.action_post()
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html("account.account_invoices", invoice.ids)[0]
            .decode()
        )
        self.assertIn("12345678901", html)
        self.assertIn("90010112345", html)
        self.assertIn("fines tributarios", html)
