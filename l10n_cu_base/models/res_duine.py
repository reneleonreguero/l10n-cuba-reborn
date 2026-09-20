from odoo import fields, models


class ResDuine(models.Model):
    _name = "res.duine"
    _description = "Directorio de Unidades Institucionales y Establecimientos"
    _order = "code"

    code = fields.Char(string="Codigo DUINE", required=True, index=True)
    name = fields.Char(string="Denominacion", required=True, index=True)
    acronym = fields.Char(string="Siglas")
    address = fields.Char(string="Direccion")
    dpa_code = fields.Char(string="Codigo DPA", index=True)
    municipality_id = fields.Many2one(
        "res.municipality", string="Municipio", ondelete="restrict"
    )
    nae_code = fields.Char(string="Codigo NAE", index=True)
    nae_name = fields.Char(string="Descripcion NAE")
    cnae_code = fields.Char(string="Codigo CNAE", index=True)
    cnae_name = fields.Char(string="Descripcion CNAE")
    cnae_id = fields.Many2one("res.cnae", string="Actividad CNAE", ondelete="restrict")
    organization_form_code = fields.Char(string="Codigo forma organizativa")
    organization_form_name = fields.Char(string="Forma organizativa", index=True)
    parent_code = fields.Char(string="Codigo de subordinacion", index=True)
    source_date = fields.Date(string="Fecha del directorio")
    active = fields.Boolean(default=True)

    _code_unique = models.Constraint(
        "unique(code)",
        "El codigo DUINE debe ser unico.",
    )
