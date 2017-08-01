# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PaymentTransactionOgone(models.Model):
    _inherit = 'payment.transaction'

    # ogone status
    _ogone_valid_tx_status = [5, 9, 56]
    _ogone_error_tx_status = {
        57: 'Not OK with scheduled payments',
        6: 'Authorised and cancelled',
    }

    def _ogone_form_validate(self, data):
        status = int(data.get('STATUS') or 0)
        if status in self._ogone_error_tx_status:
            self.write({
                'state': 'error',
                'state_message': self._ogone_error_tx_status[status],
            })
            return True

        return super(PaymentTransactionOgone, self)._ogone_form_validate(data)

    def _ogone_form_get_invalid_parameters(self, data):
        invalid_parameters = super(PaymentTransactionOgone, self)._ogone_form_get_invalid_parameters(data)

        if len(self.payment_ids) > 1:
            for parameter in invalid_parameters:
                if parameter[0] == 'amount':
                    invalid_parameters.remove(parameter)

        return invalid_parameters

