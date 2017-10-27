# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_round, float_repr
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo import models

import time
import urlparse

from odoo.addons.payment_ogone.controllers.main import OgoneController


class PaymentAcquirerOgone(models.Model):
    _inherit = 'payment.acquirer'

    def ogone_form_generate_values(self, values):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if not self.payment_term_id:
            return super(PaymentAcquirerOgone, self).ogone_form_generate_values(values)
        ogone_tx_values = dict(values)
        temp_ogone_tx_values = {
            'PSPID': self.ogone_pspid,
            'ORDERID': values['reference'],
            'AMOUNT': float_repr(float_round(values['amount'], 2) * 100, 0),
            'CURRENCY': values['currency'] and values['currency'].name or '',
            'LANGUAGE': values.get('partner_lang'),
            'CN': values.get('partner_name'),
            'EMAIL': values.get('partner_email'),
            'OWNERZIP': values.get('partner_zip'),
            'OWNERADDRESS': values.get('partner_address'),
            'OWNERTOWN': values.get('partner_city'),
            'OWNERCTY': values.get('partner_country') and values.get('partner_country').code or '',
            'OWNERTELNO': values.get('partner_phone'),
            'ACCEPTURL': '%s' % urlparse.urljoin(base_url, OgoneController._accept_url),
            'DECLINEURL': '%s' % urlparse.urljoin(base_url, OgoneController._decline_url),
            'EXCEPTIONURL': '%s' % urlparse.urljoin(base_url, OgoneController._exception_url),
            'CANCELURL': '%s' % urlparse.urljoin(base_url, OgoneController._cancel_url),
            'PARAMPLUS': 'return_url=%s' % ogone_tx_values.pop('return_url') if ogone_tx_values.get('return_url') else False,
        }
        if self.save_token in ['ask', 'always']:
            temp_ogone_tx_values.update({
                'ALIAS': 'ODOO-NEW-ALIAS-%s' % time.time(),    # something unique,
                'ALIASUSAGE': values.get('alias_usage') or self.ogone_alias_usage,
            })
        totlines = self.payment_term_id.compute(
            float_round(values['amount'], 2),
        )[0]
        index = 1
        for scheduled_date, amount in sorted(totlines):
            scheduled_date = datetime.strptime(scheduled_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
            if index == 1:
                temp_ogone_tx_values['AMOUNT1'] = float_repr(float_round(amount, 2) * 100, 0)
            else:
                temp_ogone_tx_values['AMOUNT' + str(index)] = float_repr(float_round(amount, 2) * 100, 0)
                temp_ogone_tx_values['EXECUTIONDATE' + str(index)] = scheduled_date
            index += 1
        shasign = self._ogone_generate_shasign('in', temp_ogone_tx_values)
        temp_ogone_tx_values['SHASIGN'] = shasign
        ogone_tx_values.update(temp_ogone_tx_values)
        return ogone_tx_values

