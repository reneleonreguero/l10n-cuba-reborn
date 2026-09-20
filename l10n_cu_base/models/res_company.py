from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_cu_entity_type = fields.Selection(
        string="Tipo de entidad cubana",
        related="partner_id.l10n_cu_entity_type",
        readonly=False,
        store=True,
    )
    l10n_cu_duine_id = fields.Many2one(
        "res.duine",
        string="Registro DUINE",
        related="partner_id.l10n_cu_duine_id",
        readonly=False,
        store=True,
    )
    l10n_cu_reeup = fields.Char(
        string="Codigo REEUP",
        related="partner_id.l10n_cu_reeup",
        readonly=False,
        store=True,
    )
    l10n_cu_registry_number = fields.Char(
        string="Registro Mercantil",
        related="partner_id.l10n_cu_registry_number",
        readonly=False,
        store=True,
    )
    l10n_cu_rcc_licence = fields.Char(
        string="Licencia / RCC",
        related="partner_id.l10n_cu_rcc_licence",
        readonly=False,
        store=True,
    )
