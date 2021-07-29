# -*- coding: utf-8 -*-
##########################################################################
#
#  Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#  See LICENSE file for full copyright and licensing details.
#  License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, fields, models, _


class MagentoStoreView(models.Model):
    _inherit = "magento.store.view"

    @api.model
    def syncMagento2StoreView(self, storeData):
        storeId = 0
        instanceId = self._context.get('instance_id')
        websiteId = self.getMagento2Website(storeData, instanceId)
        if websiteId:
            storeId = self.getMagentoStoreView(
                storeData, websiteId, instanceId)
        return storeId

    @api.model
    def getMagento2Website(self, storeData, instanceId):
        websiteId = 0
        websites = self.env['magento.website'].search([
            ('website_id', '=', storeData['website_id']),
            ('instance_id', '=', instanceId)])
        if websites:
            websiteId = websites[0].id
            if not websites[0].wk_pricelist:
                if storeData.get('auto_pricelist') == '1':
                    pricelistId = self.createWebsitePriceList(storeData)
                    if pricelistId:
                        websites[0].wk_pricelist = pricelistId
        else:
            websiteDict = {
                'name': storeData['website_name'],
                'code': storeData['website_code'],
                'instance_id': instanceId,
                'website_id': storeData['website_id'],
                'default_group_id': storeData['default_group_id']
            }
            if storeData.get('auto_pricelist') == '1':
                pricelistId = self.createWebsitePriceList(storeData)
                websiteDict['wk_pricelist'] = pricelistId.id
            websiteId = self.env['magento.website'].create(websiteDict)
            websiteId = websiteId.id
        return websiteId

    @api.model
    def getMagentoStoreGroup(self, storeData, websiteId, instanceId):
        groupId = 0
        views = self.env['magento.store'].search([
            ('group_id', '=', storeData['group_id']),
            ('instance_id', '=', instanceId)])
        if views:
            groupId = views[0].id
        else:
            groupDict = {
                'name': storeData['group_name'],
                'website_id': websiteId,
                'group_id': storeData['group_id'],
                'instance_id': instanceId,
                'root_category_id': storeData['root_category_id'],
                'default_store_id': storeData['default_store_id'],
            }
            groupId = self.env['magento.store'].create(groupDict)
            groupId = groupId.id
        return groupId

    @api.model
    def getMagentoStoreView(self, storeData, websiteId, instanceId):
        storeId = 0
        views = self.search([('view_id', '=', storeData[
            'store_id']), ('instance_id', '=', instanceId)])
        if views:
            storeId = views[0].id
        else:
            groupId = self.getMagentoStoreGroup(
                storeData, websiteId, instanceId)
            if groupId:
                viewDict = {
                    'name': storeData['name'],
                    'code': storeData['code'],
                    'view_id': storeData['store_id'],
                    'group_id': groupId,
                    'instance_id': instanceId,
                }
                storeId = self.create(viewDict)
                storeId = storeId.id
        return storeId

    @api.model
    def createWebsitePriceList(self, storeData):
        pricelistId = 0
        websiteCode = storeData['website_code']
        storeCode = storeData['code']
        if websiteCode and storeCode:
            pricelistData = {'name': websiteCode +
                "_" + storeCode}
            pricelistId = self.env[
                'product.pricelist'].create(pricelistData)
        return pricelistId
