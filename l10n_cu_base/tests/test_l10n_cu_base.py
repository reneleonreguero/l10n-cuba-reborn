from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nCuBase(TransactionCase):
    def test_reference_data(self):
        cuba = self.env.ref("base.cu")
        self.assertEqual(
            self.env["res.municipality"].search_count([("country_id", "=", cuba.id)]),
            168,
        )
        self.assertEqual(self.env["res.cnae"].search_count([]), 427)
        self.assertTrue(self.env.ref("base.CUP").active)

    def test_municipality_must_match_state(self):
        municipality = self.env.ref("l10n_cu_base.municipio_2101")
        partner = self.env["res.partner"].create(
            {
                "name": "Entidad de prueba",
                "country_id": self.env.ref("base.cu").id,
                "state_id": municipality.state_id.id,
                "municipality_id": municipality.id,
            }
        )
        with self.assertRaises(ValidationError):
            partner.state_id = self.env.ref("l10n_cu_base.state_23")

    def test_persona_natural_carne_identidad(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Persona natural de prueba",
                "is_company": False,
                "country_id": self.env.ref("base.cu").id,
                "l10n_cu_ci": "91082712345",
            }
        )
        self.assertFalse(partner.is_company)
        self.assertEqual(partner.l10n_cu_ci, "91082712345")

    def test_reeup_prefill_from_duine(self):
        duine = self.env["res.duine"].create(
            {"code": "45042", "name": "Mipyme de prueba"}
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Mipyme de prueba",
                "is_company": True,
                "country_id": self.env.ref("base.cu").id,
                "l10n_cu_duine_id": duine.id,
            }
        )
        partner._onchange_l10n_cu_duine_id()
        self.assertEqual(partner.l10n_cu_reeup, "45042")

    def test_nit_is_vat(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Empresa estatal de prueba",
                "is_company": True,
                "country_id": self.env.ref("base.cu").id,
                "vat": "00000001",
            }
        )
        self.assertEqual(partner.l10n_cu_nit, "00000001")
        partner.l10n_cu_nit = "00000002"
        self.assertEqual(partner.vat, "00000002")
