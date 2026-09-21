from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("state", "partner_id", "company_id", "move_type")
    def _check_l10n_cu_identifiers(self):
        for move in self:
            if (
                not move.is_invoice(include_receipts=False)
                or move.state != "posted"
                or move.company_id.country_id.code != "CU"
            ):
                continue
            if not move.company_id.partner_id.vat:
                raise ValidationError(
                    _(
                        "La compañía emisora %s no tiene NIT configurado.",
                        move.company_id.display_name,
                    )
                )
            partner = move.partner_id.commercial_partner_id
            if not partner.vat and not partner.l10n_cu_ci:
                raise ValidationError(
                    _(
                        "El receptor %s debe tener NIT (persona jurídica) "
                        "o carné de identidad (persona natural).",
                        partner.display_name,
                    )
                )
