# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class PaymentTransactionOgone(models.Model):
    _inherit = 'payment.transaction'

    # ogone status
    _ogone_valid_tx_status = [5, 9, 56]
    _ogone_error_tx_status = {
        57: 'Not OK with scheduled payments',
        6: 'Authorised and cancelled',
    }

    @api.model
    def _ogone_form_validate(self, tx, data):
        status = int(data.get('STATUS') or 0)
        if status in self._ogone_error_tx_status:
            tx.write({
                'state': 'error',
                'state_message': self._ogone_error_tx_status[status],
            })
            return True

        return super(PaymentTransactionOgone, self)._ogone_form_validate(tx, data)

    @api.model
    def _ogone_form_get_invalid_parameters(self, tx, data):
        invalid_parameters = super(PaymentTransactionOgone, self)._ogone_form_get_invalid_parameters(tx, data)

        if len(tx.payment_ids) > 1:
            for parameter in invalid_parameters:
                if parameter[0] == 'amount':
                    invalid_parameters.remove(parameter)

        return invalid_parameters

