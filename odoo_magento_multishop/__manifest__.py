# -*- coding: utf-8 -*-
##########################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##########################################################################

{
    "name": "MOB Multi Shop Extension",
    "summary": "Multi Shop Extension",
    "version": "4.0.0",
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "license": "Other proprietary",
    "website": "https://store.webkul.com/Multishop-MOB-extension.html",
    "description": """
MOB Multi Shop Extension

Synchronize store information from Magento to Odoo.

Multi Shop Features:

1. Adds Magento Store in Sales order.
2. Adds Magento websites in Products
3. Customer-group as a pricelist.

This module works very well with latest version of magento 2.* and Odoo 14.0

                        """,
    "depends": ['odoo_magento_connect'],
    "data": [
        'views/magento_store_view.xml',
        'views/magento_website_view.xml',
        'views/product_template_views.xml',
        'views/sale_views.xml',
    ],
    "application": True,
    "pre_init_hook": "pre_init_check",
}
