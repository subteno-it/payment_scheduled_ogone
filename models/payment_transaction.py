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

from openerp import models


class PaymentTransactionOgone(models.Model):
    _inherit = 'payment.transaction'

    # ogone status
    _ogone_valid_tx_status = [5, 9, 56]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
