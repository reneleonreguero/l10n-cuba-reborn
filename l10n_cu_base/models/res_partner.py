from odoo import api, fields, models
from odoo.exceptions import ValidationError


CUBAN_ENTITY_TYPES = [
    ("oace", "Organismo de la Administracion Central del Estado"),
    ("state_company", "Empresa estatal"),
    ("budget_unit", "Unidad presupuestada"),
    ("mixed_company", "Empresa mixta"),
    ("mipyme", "MIPYME"),
    ("tcp", "Trabajador por cuenta propia"),
    ("cooperative", "Cooperativa"),
    ("association", "Asociacion o fundacion"),
    ("other", "Otra"),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    municipality_id = fields.Many2one(
        "res.municipality",
        string="Municipio",
        ondelete="restrict",
        domain="[('state_id', '=', state_id)]",
    )
    municipality_name = fields.Char(
        string="Nombre del municipio", related="municipality_id.name"
    )
    l10n_cu_nit = fields.Char(string="NIT", related="vat", readonly=False)
    l10n_cu_ci = fields.Char(string="Carne de identidad")
    l10n_cu_reeup = fields.Char(string="Codigo REEUP")
    l10n_cu_registry_number = fields.Char(string="Registro Mercantil")
    l10n_cu_rcc_licence = fields.Char(string="Licencia / RCC")
    l10n_cu_entity_type = fields.Selection(CUBAN_ENTITY_TYPES, string="Tipo de entidad")
    l10n_cu_cnae_ids = fields.Many2many(
        "res.cnae", string="Actividades economicas"
    )
    l10n_cu_primary_cnae_id = fields.Many2one(
        "res.cnae", string="Actividad economica principal", ondelete="restrict"
    )
    l10n_cu_duine_id = fields.Many2one(
        "res.duine", string="Registro DUINE", ondelete="restrict"
    )

    @api.onchange("l10n_cu_duine_id")
    def _onchange_l10n_cu_duine_id(self):
        for partner in self:
            if partner.l10n_cu_duine_id and not partner.l10n_cu_reeup:
                partner.l10n_cu_reeup = partner.l10n_cu_duine_id.code

    @api.onchange("state_id")
    def _onchange_l10n_cu_state_id(self):
        for partner in self:
            if partner.municipality_id.state_id != partner.state_id:
                partner.municipality_id = False

    @api.constrains("state_id", "municipality_id")
    def _check_municipality_state(self):
        for partner in self:
            if (
                partner.municipality_id
                and partner.municipality_id.state_id != partner.state_id
            ):
                raise ValidationError(
                    "El municipio seleccionado no pertenece a la provincia indicada."
                )

    @api.constrains("l10n_cu_primary_cnae_id", "l10n_cu_cnae_ids")
    def _check_primary_cnae(self):
        for partner in self:
            if (
                partner.l10n_cu_primary_cnae_id
                and partner.l10n_cu_cnae_ids
                and partner.l10n_cu_primary_cnae_id not in partner.l10n_cu_cnae_ids
            ):
                raise ValidationError(
                    "La actividad principal debe estar entre las actividades economicas."
                )

    @api.model
    def _address_fields(self):
        return super()._address_fields() + ["municipality_name"]
