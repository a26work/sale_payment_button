from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(string='Payment Count', compute='_compute_payment_count')

    @api.depends('invoice_ids', 'invoice_ids.payment_state')
    def _compute_payment_count(self):
        for order in self:
            payment_count = 0
            invoice_ids = order.invoice_ids.filtered(
                lambda inv: inv.move_type == 'out_invoice' and inv.state != 'cancel')
            if invoice_ids:
                # In Odoo 16, payments are linked to invoices through reconciliations
                # and the payment state is stored in the related account_move
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
                    WHERE am.id IN %s
                    AND payment_move.state = 'posted'
                """, (tuple(invoice_ids.ids),))
                payment_count = self.env.cr.fetchone()[0] or 0
            order.payment_count = payment_count

    def action_view_payments(self):
        invoice_ids = self.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state != 'cancel')
        if not invoice_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Payments'),
                'res_model': 'account.payment',
                'view_mode': 'tree,form',
                'domain': [('id', '=', 0)],  # Empty domain
                'context': {'create': False},
            }

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
            WHERE am.id IN %s
            AND payment_move.state = 'posted'
        """, (tuple(invoice_ids.ids),))
        payment_ids = [payment_id[0] for payment_id in self.env.cr.fetchall()]

        # Create access token for users without full access rights
        access_token = None
        if not self.env.user.has_group('account.group_account_invoice'):
            access_token = self.env['ir.config_parameter'].sudo().get_param('database.uuid')

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Payments'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payment_ids)],
            'context': {
                'create': False,
                'default_sale_order_id': self.id,
                'access_token': access_token,
            },
        }

        if len(payment_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = payment_ids[0]

        return action

        action = {
            'type': 'ir.actions.act_window',
            'name': _('Payments'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payment_ids)],
            'context': {'create': False},
        }

        if len(payment_ids) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = payment_ids[0]

        return action