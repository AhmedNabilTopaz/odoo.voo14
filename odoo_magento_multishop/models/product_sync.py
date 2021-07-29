# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#  See LICENSE file for full copyright and licensing details.
#  License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import models


class ConnectorSnippet(models.TransientModel):
    _inherit = "connector.snippet"

    def _get_magento2_product_array(
            self,
            instance_id,
            channel,
            prod_obj,
            get_product_data,
            connection):
        getProductData = super(
            ConnectorSnippet,
            self)._get_magento2_product_array(
            instance_id,
            channel,
            prod_obj,
            get_product_data,
            connection)
        extension_attributes = getProductData.get('extension_attributes', {})
        extension_attributes.update({
            'website_ids': prod_obj.wk_websites_id.mapped('website_id')})
        getProductData['extension_attributes'] = extension_attributes
        return getProductData
