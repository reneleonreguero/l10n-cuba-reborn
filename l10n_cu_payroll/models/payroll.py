from odoo import _, api, fields, models
from odoo.exceptions import UserError

# Tasas de referencia de la normativa laboral y tributaria cubana.
# Deben validarse contra las disposiciones vigentes (Código de Trabajo,
# Ley 105/2008 de Seguridad Social, Ley 113/2012) antes de su uso productivo.
# El módulo las trata como parámetros editables por lote y por nómina.
VACATION_RATE = 9.09
SS_WORKER_RATE = 5.0
SS_EMPLOYER_RATE = 12.5


class L10nCuPayrollContract(models.Model):
    _name = "l10n_cu_payroll.contract"
    _description = "Ficha salarial cubana"

    name = fields.Char(required=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    wage = fields.Monetary(required=True, string="Salario mensual")
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    date_start = fields.Date(string="Fecha de inicio")
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name") and vals.get("employee_id"):
                employee = self.env["hr.employee"].browse(vals["employee_id"])
                vals["name"] = _("Ficha de %s", employee.name)
        return super().create(vals_list)


class L10nCuPayrollSlip(models.Model):
    _name = "l10n_cu_payroll.slip"
    _description = "Nómina individual cubana"

    batch_id = fields.Many2one(
        "l10n_cu_payroll.batch", required=True, ondelete="cascade"
    )
    contract_id = fields.Many2one("l10n_cu_payroll.contract", required=True)
    employee_id = fields.Many2one(
        "hr.employee", related="contract_id.employee_id", readonly=True, store=True
    )
    company_id = fields.Many2one(
        "res.company", related="batch_id.company_id", readonly=True, store=True
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    wage = fields.Monetary(required=True, string="Salario devengado")
    vacation_rate = fields.Float(default=VACATION_RATE, string="% Vacaciones")
    ss_worker_rate = fields.Float(default=SS_WORKER_RATE, string="% SS trabajador")
    ss_employer_rate = fields.Float(
        default=SS_EMPLOYER_RATE, string="% SS empleador"
    )
    other_deductions = fields.Monetary(
        default=0.0, string="Otras retenciones"
    )
    vacation_amount = fields.Monetary(
        compute="_compute_amounts", store=True, string="Provisión vacaciones"
    )
    ss_worker = fields.Monetary(
        compute="_compute_amounts", store=True, string="SS trabajador"
    )
    ss_employer = fields.Monetary(
        compute="_compute_amounts", store=True, string="SS empleador"
    )
    net = fields.Monetary(compute="_compute_amounts", store=True, string="Neto a pagar")
    state = fields.Selection(
        [("draft", "Borrador"), ("done", "Contabilizada")],
        default="draft",
        required=True,
    )

    @api.depends(
        "wage", "vacation_rate", "ss_worker_rate", "ss_employer_rate",
        "other_deductions",
    )
    def _compute_amounts(self):
        for slip in self:
            rnd = slip.currency_id.round
            slip.vacation_amount = rnd(slip.wage * slip.vacation_rate / 100.0)
            slip.ss_worker = rnd(slip.wage * slip.ss_worker_rate / 100.0)
            slip.ss_employer = rnd(slip.wage * slip.ss_employer_rate / 100.0)
            slip.net = rnd(slip.wage - slip.ss_worker - slip.other_deductions)


class L10nCuPayrollBatch(models.Model):
    _name = "l10n_cu_payroll.batch"
    _description = "Lote mensual de nómina cubana"

    name = fields.Char(required=True, default="Nómina")
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    date_from = fields.Date(required=True, string="Desde")
    date_to = fields.Date(required=True, string="Hasta")
    journal_id = fields.Many2one(
        "account.journal",
        required=True,
        string="Diario",
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]",
    )
    expense_account_id = fields.Many2one(
        "account.account",
        required=True,
        string="Cuenta de gasto salarial",
        domain="[('company_ids', 'in', company_id), "
        "('account_type', 'in', ('expense', 'expense_direct_cost'))]",
        default=lambda self: self._default_expense_account(),
    )
    slip_ids = fields.One2many("l10n_cu_payroll.slip", "batch_id")
    move_id = fields.Many2one("account.move", readonly=True, string="Asiento")
    state = fields.Selection(
        [("draft", "Borrador"), ("done", "Contabilizado")],
        default="draft",
        required=True,
    )

    @api.model
    def _default_expense_account(self):
        company = self.env.company
        return (
            self.env["account.account"]
            .with_company(company)
            .search(
                [("company_ids", "in", company.ids), ("code", "=", "826")],
                limit=1,
            )
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "Nómina") == "Nómina" and vals.get("date_from"):
                vals["name"] = _("Nómina %s", vals["date_from"][:7])
        return super().create(vals_list)

    def _payable_account(self, code):
        account = (
            self.env["account.account"]
            .with_company(self.company_id)
            .search(
                [("company_ids", "in", self.company_id.ids), ("code", "=", code)],
                limit=1,
            )
        )
        if not account:
            raise UserError(_("La compañía no tiene la cuenta %s.", code))
        return account

    def action_post(self):
        self.ensure_one()
        if self.state == "done":
            raise UserError(_("El lote ya está contabilizado."))
        if not self.slip_ids:
            raise UserError(_("El lote no tiene nóminas."))
        contracts = self.slip_ids.mapped("contract_id")
        if len(contracts) != len(self.slip_ids):
            raise UserError(_("Hay contratos duplicados en el lote."))
        for slip in self.slip_ids:
            if slip.company_id != self.company_id:
                raise UserError(_("Todas las nóminas deben ser de la compañía."))
            if slip.wage <= 0:
                raise UserError(
                    _("La nómina de %s no tiene salario.", slip.employee_id.name)
                )
        rnd = self.currency_id.round
        wages = rnd(sum(self.slip_ids.mapped("wage")))
        vacations = rnd(sum(self.slip_ids.mapped("vacation_amount")))
        ss_worker = rnd(sum(self.slip_ids.mapped("ss_worker")))
        others = rnd(sum(self.slip_ids.mapped("other_deductions")))
        ss_employer = rnd(sum(self.slip_ids.mapped("ss_employer")))
        net = rnd(sum(self.slip_ids.mapped("net")))
        retentions = rnd(ss_worker + others)
        expense_account = (
            self.env["account.account"]
            .with_company(self.company_id)
            .search(
                [
                    ("company_ids", "in", self.company_id.ids),
                    ("code", "=", self.expense_account_id.code),
                ],
                limit=1,
            )
        )
        if not expense_account:
            raise UserError(
                _("La compañía no tiene la cuenta %s.",
                  self.expense_account_id.code)
            )
        payroll_payable = self._payable_account("455")
        retentions_payable = self._payable_account("460")
        social_security = self._payable_account("440.0008")
        vacation_provision = self._payable_account("492")
        move = self.env["account.move"].create(
            {
                "company_id": self.company_id.id,
                "journal_id": self.journal_id.id,
                "date": self.date_to,
                "ref": self.name,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": _("Salarios %s", self.name),
                            "account_id": expense_account.id,
                            "debit": rnd(wages + vacations + ss_employer),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _("Neto %s", self.name),
                            "account_id": payroll_payable.id,
                            "credit": net,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _("Retenciones %s", self.name),
                            "account_id": retentions_payable.id,
                            "credit": retentions,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _("Seguridad Social %s", self.name),
                            "account_id": social_security.id,
                            "credit": ss_employer,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _("Vacaciones %s", self.name),
                            "account_id": vacation_provision.id,
                            "credit": vacations,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        self.slip_ids.write({"state": "done"})
        self.write({"move_id": move.id, "state": "done"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }
