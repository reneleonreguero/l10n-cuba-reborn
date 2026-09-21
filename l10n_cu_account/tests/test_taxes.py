from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCubanInvoiceTaxes(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create(
            {
                "name": "Empresa Tributos CU Test",
                "country_id": cls.env.ref("base.cu").id,
                "currency_id": cls.env.ref("base.CUP").id,
            }
        )
        cls.env["account.chart.template"].try_loading("cu_494_public", cls.company)
        cls.partner = cls.env["res.partner"].create({"name": "Cliente de prueba"})

    def _tax(self, xml_id):
        return self.env["account.tax"].with_company(self.company).search(
            [("company_id", "=", self.company.id), ("name", "ilike", xml_id)],
            limit=1,
        )

    def _invoice(self, move_type, amount, tax, fiscal_position=None):
        values = {
            "company_id": self.company.id,
            "move_type": move_type,
            "partner_id": self.partner.id,
            "invoice_line_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Venta de prueba",
                        "quantity": 1,
                        "price_unit": amount,
                        "tax_ids": [(6, 0, tax.ids)],
                    },
                )
            ],
        }
        if fiscal_position:
            values["fiscal_position_id"] = fiscal_position.id
        return self.env["account.move"].with_company(self.company).create(values)

    def test_iventas_taxes_loaded(self):
        iventas_10 = self._tax("I. Ventas 10%")
        iventas_2 = self._tax("I. Ventas 2%")
        self.assertEqual(iventas_10.amount, 10.0)
        self.assertEqual(iventas_10.type_tax_use, "sale")
        self.assertEqual(iventas_2.amount, 2.0)
        self.assertEqual(
            iventas_10.invoice_repartition_line_ids.filtered(
                lambda line: line.repartition_type == "tax"
            ).account_id.code,
            "440.0001",
        )

    def test_iventas_10_computed_on_sale_invoice(self):
        invoice = self._invoice(
            "out_invoice", 1000.0, self._tax("I. Ventas 10%")
        )
        self.assertEqual(invoice.amount_untaxed, 1000.0)
        self.assertEqual(invoice.amount_tax, 100.0)
        self.assertEqual(invoice.amount_total, 1100.0)

    def test_wholesale_fiscal_position_removes_iventas(self):
        fiscal_position = (
            self.env["account.fiscal.position"]
            .with_company(self.company)
            .search(
                [
                    ("company_id", "=", self.company.id),
                    ("name", "ilike", "mayorista"),
                ],
                limit=1,
            )
        )
        self.assertTrue(fiscal_position)
        exento = self._tax("Exento 0% (ventas)")
        self.assertIn(exento, fiscal_position.tax_ids)
        self.assertIn(
            self._tax("I. Ventas 10%"), exento.original_tax_ids
        )
        invoice = self._invoice(
            "out_invoice",
            1000.0,
            self._tax("I. Ventas 10%"),
            fiscal_position=fiscal_position,
        )
        for line in invoice.invoice_line_ids:
            line.tax_ids = fiscal_position.map_tax(line.tax_ids)
        self.assertEqual(invoice.amount_tax, 0.0)
        self.assertEqual(invoice.amount_total, 1000.0)

    def test_is_withholding_on_purchase_invoice(self):
        invoice = self._invoice(
            "in_invoice", 1000.0, self._tax("Retención IS 5%")
        )
        self.assertEqual(invoice.amount_tax, 50.0)
        tax_line = invoice.line_ids.filtered(
            lambda line: line.tax_line_id.name == "Retención IS 5% (TCP)"
            or line.account_id.code == "440.0005"
        )
        self.assertTrue(tax_line)

    def test_private_chart_inherits_invoice_taxes(self):
        company = self.env["res.company"].create(
            {
                "name": "Mipyme Tributos CU Test",
                "country_id": self.env.ref("base.cu").id,
                "currency_id": self.env.ref("base.CUP").id,
            }
        )
        self.env["account.chart.template"].try_loading("cu_494_private", company)
        taxes = self.env["account.tax"].search([("company_id", "=", company.id)])
        self.assertTrue(taxes.filtered(lambda tax: tax.name == "I. Ventas 10% (minorista)"))
        self.assertTrue(
            taxes.filtered(lambda tax: tax.name == "Retención IS 5% (TCP)")
        )
