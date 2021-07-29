# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#  See LICENSE file for full copyright and licensing details.
#  License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    wk_websites_id = fields.Many2many(
        'magento.website',
        'wk_website_rel',
        'store_id',
        'group_id',
        string='Websites')

    def update_vals(self, vals, instance_id, create=False):
        ctx = dict(self._context or {})
        if 'magento2' in ctx and 'wk_website_ids' in vals:
            wkWebsitesId = vals.pop('wk_website_ids', [])
            if wkWebsitesId:
                odooIds = self.env['magento.website'].search([
                    ('website_id', 'in', wkWebsitesId),
                    ('instance_id', '=', instance_id)
                ]).ids
            else:
                odooIds = []
            vals['wk_websites_id'] = [(6, 0, odooIds)]
        return super(ProductTemplate, self).update_vals(vals, instance_id, create)
