# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from urllib.parse import quote

from odoo import api, models

def _unescape(text):
    ##
    # Replaces all encoded characters by urlib with plain utf8 string.
    #
    # @param text source text.
    # @return The plain text.
    from urllib.parse import unquote_plus
    try:
        text = unquote_plus(text)
        return text
    except Exception as e:
        return text


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def magento2_stock_update(self, odoo_product_id, warehouseId):
        ctx = dict(self._context or {})
        mappingObj = self.env['connector.product.mapping'].search(
            [('name', '=', odoo_product_id)], limit=1)
        sku = mappingObj.name.default_code
        if mappingObj:
            instanceObj = mappingObj.instance_id
            mageProductId = mappingObj.ecomm_id
            stockItemId = mappingObj.magento_stock_id
            if mappingObj.instance_id.warehouse_id.id == warehouseId:
                ctx['warehouse'] = warehouseId
                productObj = self.env['product.product'].with_context(
                    ctx).browse(odoo_product_id)
                if ctx.get('mob_stock_action_val') == self.env['connector.instance'].connector_stock_action:
                    productQuantity = productObj.qty_available
                else:
                    productQuantity = productObj.virtual_available + productObj.outgoing_qty
                if instanceObj.inventory_sync == 'enable':
                    self.synch_magento2_quantity(mageProductId, productQuantity, sku, stockItemId, instanceObj)
        return True

    @api.model
    def synch_magento2_quantity(self, mageProductId, productQuantity, sku, stockItemId, instanceObj):
        response = self.update_magento2_quantity(
            mageProductId, productQuantity, sku, stockItemId, instanceObj)
        if response[0] == 1:
            return True
        else:
            self.env['connector.sync.history'].create(
                {'status': 'no', 'action_on': 'product', 'action': 'c', 'error_message': response[1]})
            return False

    @api.model
    def update_magento2_quantity(self, mageProductId, productQuantity, sku, stockItemId, instanceObj):
        text = ''
        ctx = dict(self._context or {})
        ctx['instance_id'] = instanceObj.id
        try:
            sku = quote(sku, safe='')
        except Exception as e:
            sku = quote(sku.encode("utf-8"), safe='')
        if mageProductId:
            if not instanceObj.active:
                return [
                    0, ' Connection needs one Active Configuration setting.']
            else:
                try:
                    if type(productQuantity) == str:
                        productQuantity = productQuantity.split('.')[0]
                    if type(productQuantity) == float:
                        productQuantity = productQuantity.as_integer_ratio()[0]
                    productData = {"product": {
                        'id': mageProductId,
                        'extension_attributes': {'stock_item': {
                            'itemId': stockItemId,
                            'stock_id': 1,
                            'qty': productQuantity,
                            'is_in_stock': True if productQuantity > 0 else False
                        }}
                    }}

                    connection = self.env['connector.instance'].with_context(ctx)._create_connection()
                    status = connection.get('status', False)

                    prodResponse = self.env['connector.snippet'].callMagentoApi(
                        baseUrl=connection.get('url', ''),
                        url='/V1/odoomagentoconnect/products',
                        method='post',
                        token=connection.get('token', ''),
                        data=productData
                    )
                    if not prodResponse:
                        return [0, ' Error in Updating Quantity for Magneto Product Id %s,Check synchronization history.' % (mageProductId)]
                    return [1, '']
                except Exception as e:
                    return [0, ' Error in Updating Quantity for Magneto Product Id %s, Reason >>%s' % (mageProductId,str(e))]
        else:
            return [0, 'Error in Updating Stock, Magento Product Id Not Found!!!']

    @api.model
    def check_warehouse(self, odoo_product_id, warehouse_id, ecomm_channels):
        instanceObj = self.env['connector.instance'].search([('active','=',True),('ecomm_type','=', 'magento2')], limit=1)
        if 'magento2' in ecomm_channels and instanceObj.manage_multi_source:
            self.magento_multi_stock_update(odoo_product_id, warehouse_id)
        else:
            return super(StockMove,self).check_warehouse(odoo_product_id, warehouse_id, ecomm_channels)

    @api.model
    def magento_multi_stock_update(self, odooProductId, warehouseId):
        url = ''
        ctx = dict(self._context or {})
        mappingObj = self.env['connector.product.mapping'].search([('name', '=', odooProductId)], limit=1)
        if mappingObj:
            mageProductId = mappingObj.ecomm_id
            sku = _unescape(mappingObj.name.default_code)
            instanceObj = mappingObj.instance_id
            ctx['instance_id'] = instanceObj.id
    
            if instanceObj.warehouse_id.id == warehouseId and instanceObj.active:
                locationId = self.location_id.id
                locationDestId = self.location_dest_id.id
                destSourceCode = self.env['magento.source'].search([('odoo_location', '=', locationDestId)], limit=1).mage_source_code
                originSourceCode = self.env['magento.source'].search([('odoo_location', '=', locationId)], limit=1).mage_source_code
                if originSourceCode and destSourceCode:
                        data={
                                'originSourceCode': originSourceCode, 
                                'destinationSourceCode': destSourceCode, 
                                'items':[{'sku': sku, 'qty': self.product_uom_qty}]
                                }
                        url = '/V1/inventory/bulk-partial-source-transfer'
                else:
                    location = locationDestId if destSourceCode else locationId
                    proQty = self.env['product.product'].get_theoretical_quantity(odooProductId, location)
                    data = {'sourceItems':[
                                {'sku': sku, 'source_code': destSourceCode or originSourceCode, 'quantity': proQty, 'status': 1}
                                ]}
                    url = '/V1/inventory/source-items'

                connection = self.env['connector.instance'].with_context(ctx)._create_connection()
                if url:
                    prodResponse = self.env['connector.snippet'].callMagentoApi(
                            baseUrl=connection.get('url', ''),
                            url=url,
                            method='post',
                            token=connection.get('token', ''),
                            data=data
                        )
        return True
