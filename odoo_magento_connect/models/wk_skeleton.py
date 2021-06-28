# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models


class WkSkeleton(models.TransientModel):
    _inherit = "wk.skeleton"
    _description = " Skeleton for all XML RPC imports in Odoo"

    @api.model
    def get_ecomm_href(self, getcommtype=False):
        href_list = super(WkSkeleton, self).get_ecomm_href(getcommtype)
        href_list = {}
        if getcommtype=='magento2':
            href_list = {
                'user_guide':'https://webkul.com/blog/odoo-bridge-for-magento-v2',
                'rate_review':'https://store.webkul.com/Odoo-Bridge-For-Magento2.html',
                'extension':'https://store.webkul.com/Magento-2/Odoo-ERP.html',
                'name' : 'MAGENTO',
                'short_form' : 'MOB',
                'img_link' : '/odoo_magento_connect/static/src/img/magento-logo.png'
            }
        return href_list

    @api.model
    def set_source_order_shipped(self, orderId, shipVals):
        """Ship the order in Odoo via requests from XML-RPC
        @param order_id: Odoo Order ID
        @param shipVals: Shipping products data containing magento sources
        @param context: Mandatory Dictionary with key 'ecommerce' to identify the request from E-Commerce
        @return:  A dictionary of status and status message of transaction"""

        status = True
        ctx = dict(self._context or {})
        status_message = "Order Successfully Shipped."
        try:
            saleObj = self.env['sale.order'].browse(orderId)
            backOrderModel = self.env['stock.backorder.confirmation']
            if saleObj.state == 'draft':
                self.confirm_odoo_order([orderId])
            if saleObj.picking_ids:
                for pickingObj in saleObj.picking_ids.filtered(
                        lambda pickingObj: pickingObj.picking_type_code == 'outgoing' and pickingObj.state != 'done'):
                    location_id = self.env['magento.source'].search([('mage_source_code', '=', shipVals[0].get('source_code'))]).odoo_location.id
                    ctx['active_id'] = pickingObj.id
                    ctx['picking_id'] = pickingObj.id
                    pickingObj.action_assign()
                    for packObj in pickingObj.move_line_ids_without_package:
                        if packObj.product_uom_qty > 0:
                            qtyShip = [ship['product_qty'] for ship in shipVals if ship['product_id'] == packObj.product_id.id]
                            packObj.write({'qty_done': qtyShip[0], 'location_id': location_id if location_id else packObj.location_id})
                        else:
                            packObj.unlink()
                    if pickingObj._check_backorder():
                        backorderObj = backOrderModel.create({'pick_ids': [(4, pickingObj.id)]})
                        backorderObj.process()
                    else:
                        pickingObj.button_validate()
                    self.with_context(ctx).set_extra_values()
        except Exception as e:
            status = False
            status_message = "Error in Delivering Order: %s" % str(e)
            _logger.info('## Exception set_source_order_shipped(%s) : %s' % (orderId, status_message))
        finally:
            return {
                'status_message': status_message,
                'status': status
            }
