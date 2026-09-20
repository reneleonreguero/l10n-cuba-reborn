from odoo import api, fields, models


class ResCnae(models.Model):
    _name = "res.cnae"
    _description = "Clasificador Nacional de Actividades Economicas"
    _order = "code"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "unique(code)",
        "El codigo CNAE debe ser unico.",
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.code} - {record.name}"
