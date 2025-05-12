from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_count = fields.Integer(string='Payment Count', compute='_compute_payment_count')

    @api.depends('state', 'payment_state')
    def _compute_payment_count(self):
        for move in self:
            payment_count = 0
            if move.is_invoice() and move.state == 'posted':
                # Get payments related to this invoice through reconciliations
                self.env.cr.execute("""
                    SELECT COUNT(DISTINCT ap.id)
                    FROM account_payment ap
                    JOIN account_move_line aml ON ap.id = aml.payment_id
                    JOIN account_partial_reconcile apr ON (aml.id = apr.credit_move_id OR aml.id = apr.debit_move_id)
                    JOIN account_move_line aml2 ON (
                        (aml2.id = apr.debit_move_id AND aml.id = apr.credit_move_id) OR
                        (aml2.id = apr.credit_move_id AND aml.id = apr.debit_move_id)
                    )
                    JOIN account_move am ON aml2.move_id = am.id
                    JOIN account_move payment_move ON payment_move.id = aml.move_id
                    WHERE am.id = %s
                    AND payment_move.state = 'posted'
                """, (move.id,))
                payment_count = self.env.cr.fetchone()[0] or 0
            move.payment_count = payment_count

    def action_view_payments(self):
        if not self.is_invoice():
            return {
                'type': 'ir.actions.act_window',
                'name': _('Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('id', '=', 0)],  # Empty domain
                'context': {'create': False},
            }

        # Get all payment ids related to this invoice through reconciliations
        self.env.cr.execute("""
            SELECT DISTINCT ap.id
            FROM account_payment ap
            JOIN account_move_line aml ON ap.id = aml.payment_id
            JOIN account_partial_reconcile apr ON (aml.id = apr.credit_move_id OR aml.id = apr.debit_move_id)
            JOIN account_move_line aml2 ON (
                (aml2.id = apr.debit_move_id AND aml.id = apr.credit_move_id) OR
                (aml2.id = apr.credit_move_id AND aml.id = apr.debit_move_id)
            )
            JOIN account_move am ON aml2.move_id = am.id
            JOIN account_move payment_move ON payment_move.id = aml.move_id
            WHERE am.id = %s
            AND payment_move.state = 'posted'
        """, (self.id,))
        payment_ids = [payment_id[0] for payment_id in self.env.cr.fetchall()]

        # Create access token for users without full access rights
        access_token = None
        if not self.env.user.has_group('account.group_account_invoice'):
            access_token = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

            # For sales users, also pass the sale order ID if available
            sale_order_id = self.env['sale.order'].search([('invoice_ids', 'in', self.ids)], limit=1)
            if sale_order_id:
                sale_order_id = sale_order_id.id

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Payments'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payment_ids)],
            'context': {
                'create': False,
                'access_token': access_token,
            },
        }

        if len(payment_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = payment_ids[0]

        return action