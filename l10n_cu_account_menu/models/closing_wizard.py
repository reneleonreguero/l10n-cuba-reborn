from odoo import _, fields, models
from odoo.exceptions import UserError


class L10nCuClosingWizard(models.TransientModel):
    _name = "l10n_cu_closing_wizard"
    _description = "Asistente de cierre anual cubano"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    date_to = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(month=12, day=31),
        string="Fecha de cierre",
    )
    journal_id = fields.Many2one(
        "account.journal",
        required=True,
        string="Diario de cierre",
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
    )
    post_move = fields.Boolean(
        default=True,
        string="Publicar el asiento",
    )
    lock_period = fields.Boolean(
        default=True,
        string="Bloquear el período hasta la fecha de cierre",
    )
    move_id = fields.Many2one(
        "account.move",
        readonly=True,
        string="Asiento de cierre",
    )

    def action_generate(self):
        self.ensure_one()
        company = self.company_id
        nominals = (
            self.env["account.move.line"]
            .with_company(company)
            .search_read(
            [
                ("company_id", "=", company.id),
                ("parent_state", "=", "posted"),
                ("date", "<=", self.date_to),
                ("account_id.account_type", "in", ("income", "expense")),
            ],
            ["account_id", "balance"],
        )
        )
        balances = {}
        for item in nominals:
            account_id = item["account_id"][0]
            balances[account_id] = balances.get(account_id, 0.0) + item["balance"]
        balances = {
            account_id: balance
            for account_id, balance in balances.items()
            if not company.currency_id.is_zero(balance)
        }
        if not balances:
            raise UserError(
                _("No hay saldos nominales (ingresos o gastos) que cerrar.")
            )
        resultado = (
            self.env["account.account"].with_company(company).search(
            [
                ("company_ids", "in", company.ids),
                ("code", "=", "999"),
                ("account_type", "=", "equity_unaffected"),
            ],
            limit=1,
        )
        )
        if not resultado:
            raise UserError(
                _("La compañía no tiene la cuenta 999 Resultado.")
            )
        Account = self.env["account.account"].with_company(company)
        lines = []
        for account_id, balance in sorted(balances.items()):
            account = Account.browse(account_id)
            if balance > 0:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "name": _("Cierre anual: %s", account.code),
                            "account_id": account.id,
                            "credit": balance,
                        },
                    )
                )
            else:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "name": _("Cierre anual: %s", account.code),
                            "account_id": account.id,
                            "debit": -balance,
                        },
                    )
                )
        net = sum(balances.values())
        if net > 0:
            lines.append(
                (
                    0,
                    0,
                    {
                        "name": _("Cierre anual: resultado"),
                        "account_id": resultado.id,
                        "debit": net,
                    },
                )
            )
        else:
            lines.append(
                (
                    0,
                    0,
                    {
                        "name": _("Cierre anual: resultado"),
                        "account_id": resultado.id,
                        "credit": -net,
                    },
                )
            )
        move = self.env["account.move"].create(
            {
                "company_id": company.id,
                "journal_id": self.journal_id.id,
                "date": self.date_to,
                "ref": _("Cierre anual %s", self.date_to.year),
                "line_ids": lines,
            }
        )
        if self.post_move:
            move.action_post()
        if self.lock_period:
            company.fiscalyear_lock_date = self.date_to
        self.move_id = move.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }
