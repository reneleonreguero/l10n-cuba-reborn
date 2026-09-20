from odoo import fields, models


class ResMunicipality(models.Model):
    _name = "res.municipality"
    _description = "Municipio"
    _order = "code"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, index=True)
    country_id = fields.Many2one(
        "res.country", required=True, index=True, ondelete="restrict"
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="Provincia",
        required=True,
        index=True,
        ondelete="restrict",
        domain="[('country_id', '=', country_id)]",
    )
    active = fields.Boolean(default=True)

    _code_country_unique = models.Constraint(
        "unique(code, country_id)",
        "El codigo del municipio debe ser unico por pais.",
    )


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    municipality_ids = fields.One2many(
        "res.municipality", "state_id", string="Municipios"
    )
