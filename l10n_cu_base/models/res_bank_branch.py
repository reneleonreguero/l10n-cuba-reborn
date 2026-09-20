from odoo import fields, models


class ResBankBranch(models.Model):
    _name = "res.bank.branch"
    _description = "Sucursal bancaria"
    _order = "bank_id, code"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    bank_id = fields.Many2one(
        "res.bank", string="Banco", required=True, index=True, ondelete="cascade"
    )
    bic = fields.Char(string="BIC/SWIFT", related="bank_id.bic", readonly=True)
    street = fields.Char(string="Direccion")
    street2 = fields.Char(string="Direccion 2")
    municipality_id = fields.Many2one(
        "res.municipality", string="Municipio", ondelete="restrict"
    )
    state_id = fields.Many2one(
        "res.country.state", string="Provincia", ondelete="restrict"
    )
    zip = fields.Char(string="Codigo postal")
    phone = fields.Char(string="Telefono")
    active = fields.Boolean(default=True)

    _bank_code_unique = models.Constraint(
        "unique(bank_id, code)",
        "El codigo de sucursal debe ser unico por banco.",
    )


class ResBank(models.Model):
    _inherit = "res.bank"

    branch_ids = fields.One2many("res.bank.branch", "bank_id", string="Sucursales")
