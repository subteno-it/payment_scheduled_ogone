# -*- coding: utf-8 -*-
##############################################################################
#
#    payment_scheduled_ogone module for OpenERP, Allows customers to pay for a purchase in several instalments
#    Copyright (C) 2016 SYLEAM Info Services (<http://www.syleam.fr>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of payment_scheduled_ogone
#
#    payment_scheduled_ogone is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    payment_scheduled_ogone is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
