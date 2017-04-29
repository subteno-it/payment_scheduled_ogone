# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM Info Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_round, float_repr
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from hashlib import sha1
from odoo import models

import time
import urlparse

from odoo.addons.payment_ogone.controllers.main import OgoneController


class PaymentAcquirerOgone(models.Model):
    _inherit = 'payment.acquirer'

    def _ogone_generate_shasign(self, inout, values):
        """ Generate the shasign for incoming or outgoing communications.

        :param string inout: 'in' (odoo contacting ogone) or 'out' (ogone
                             contacting odoo). In this last case only some
                             fields should be contained (see e-Commerce basic)
        :param dict values: transaction values

        :return string: shasign
        """
        assert inout in ('in', 'out')
        assert self.provider == 'ogone'
        key = getattr(self, 'ogone_shakey_' + inout)

        def filter_key(key):
            if inout == 'in':
                return True
            else:
                # SHA-OUT keys
                # source https://viveum.v-psp.com/Ncol/Viveum_e-Com-BAS_EN.pdf
                keys = [
                    'AAVADDRESS',
                    'AAVCHECK',
                    'AAVMAIL',
                    'AAVNAME',
                    'AAVPHONE',
                    'AAVZIP',
                    'ACCEPTANCE',
                    'ALIAS',
                    'AMOUNT',
                    'AMOUNT1',
                    'AMOUNT2',
                    'AMOUNT3',
                    'BIC',
                    'BIN',
                    'BRAND',
                    'CARDNO',
                    'CCCTY',
                    'CN',
                    'COMPLUS',
                    'CREATION_STATUS',
                    'CURRENCY',
                    'CVCCHECK',
                    'DCC_COMMPERCENTAGE',
                    'DCC_CONVAMOUNT',
                    'DCC_CONVCCY',
                    'DCC_EXCHRATE',
                    'DCC_EXCHRATESOURCE',
                    'DCC_EXCHRATETS',
                    'DCC_INDICATOR',
                    'DCC_MARGINPERCENTAGE',
                    'DCC_VALIDHOURS',
                    'DIGESTCARDNO',
                    'ECI',
                    'ED',
                    'ENCCARDNO',
                    'EXECUTIONDATE2',
                    'EXECUTIONDATE3',
                    'FXAMOUNT',
                    'FXCURRENCY',
                    'IBAN',
                    'IP',
                    'IPCTY',
                    'NBREMAILUSAGE',
                    'NBRIPUSAGE',
                    'NBRIPUSAGE_ALLTX',
                    'NBRUSAGE',
                    'NCERROR',
                    'NCERRORCARDNO',
                    'NCERRORCN',
                    'NCERRORCVC',
                    'NCERRORED',
                    'ORDERID',
                    'PAYID',
                    'PAYIDSUB',
                    'PM',
                    'SCO_CATEGORY',
                    'SCORING',
                    'STATUS',
                    'SUBBRAND',
                    'SUBSCRIPTION_ID',
                    'TRXDATE',
                    'VC'
                ]
                return key.upper() in keys

        items = sorted((k.upper(), v) for k, v in values.items())
        sign = ''.join('%s=%s%s' % (k, v, key) for k, v in items if v and filter_key(k))
        sign = sign.encode("utf-8")
        shasign = sha1(sign).hexdigest()
        return shasign

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

