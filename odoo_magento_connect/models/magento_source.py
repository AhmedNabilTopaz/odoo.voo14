# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################


from odoo import api, fields, models


class MagentoSource(models.Model):
    _name = "magento.source"

    odoo_location = fields.Many2one( 'stock.location', string="Odoo Location")
    mage_source_code = fields.Char(string='Magento Source Code')
    instance_id = fields.Many2one('connector.instance', string='Connector Instance')
    created_by = fields.Char(string='Created By', default="Magento-Front", size=64)
    create_date = fields.Datetime(string='Created Date', readonly=True)
