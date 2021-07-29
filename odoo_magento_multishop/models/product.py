# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#  See LICENSE file for full copyright and licensing details.
#  License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        wkPriceList = []
        if 'magento2' in self._context:
            wkPriceList = vals.pop("wk_price_list", False)
        productObj = super(ProductProduct, self).create(vals)
        productObj.updateMagento2PriceList(wkPriceList)
        return productObj

    def write(self, vals):
        wkPriceList = []
        if 'magento2' in self._context:
            wkPriceList = vals.pop("wk_price_list", False)
        res = super(ProductProduct, self).write(vals)
        self.updateMagento2PriceList(wkPriceList)
        return res

    def updateMagento2PriceList(self, wkPriceList):
        ctx = dict(self._context or {})
        if wkPriceList:
            instanceId = ctx.get('instance_id')
            self.manageMagento2Pricelist(self._ids, wkPriceList, instanceId)
        return True

    @api.model
    def manageMagento2Pricelist(self, prodIds, wkPriceList, instanceId):
        magWebModel = self.env['magento.website']
        for websiteId, websitePrice in wkPriceList.items():
            mappedWebsiteObj = magWebModel.search([
                ('website_id', '=', int(websiteId)),
                ('instance_id', '=', instanceId)
            ], limit=1)
            if mappedWebsiteObj:
                websitePriceListId = mappedWebsiteObj.wk_pricelist.id
                self.createMagento2Pricelist(
                    websitePriceListId, websitePrice, prodIds)

    @api.model
    def createMagento2Pricelist(self, websitePriceListId, websitePrice, prodIds):
        pricelistItemModel = self.env['product.pricelist.item']
        if websitePriceListId:
            pricelistItemObj = pricelistItemModel.search([
                ('pricelist_id', '=', websitePriceListId),
                ('product_id', 'in', prodIds)
            ])
            if pricelistItemObj:
                pricelistItemObj.write({'fixed_price': websitePrice})
                existProIds = pricelistItemObj.mapped('product_id.id')
            else:
                existProIds = []

            remainProdIds = list(set(prodIds) - set(existProIds))
            for productId in remainProdIds:
                pricelistItemModel.create(dict(
                    pricelist_id=websitePriceListId,
                    product_id=productId,
                    fixed_price=websitePrice,
                    applied_on='0_product_variant'
                ))
        return True

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
        return super(ProductProduct, self).update_vals(vals, instance_id, create)
