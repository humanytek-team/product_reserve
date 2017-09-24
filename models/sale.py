# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017 Humanytek (<www.humanytek.com>).
#    Rubén Bravo <rubenred18@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = 'sale.order.line'

    product_default_code = fields.Char(related='product_id.default_code',
                              string='Default Code', readonly=True, store=False)
    product_brand = fields.Char(related='product_id.product_brand_id.name',
                              string='Brand', readonly=True, store=False)
    product_categ = fields.Char(related='product_id.categ_id.name',
                              string='Category', readonly=True, store=False)
    mrp_id = fields.Many2one(
        'mrp.production',
        compute='_compute_mrp_info',
        string='MRP Production',
        readonly=True,
        store=False)
    mrp_move_raw_ids = fields.One2many(related='mrp_id.move_raw_ids',
                              string='Moves', readonly=True, store=False)

    @api.multi
    def _compute_mrp_info(self):
        self.mrp_id = self.env['mrp.production'].search([
                                    ('sale_id', '=', self.order_id.id),
                                    ('product_id', '=', self.product_id.id),
                                    ('state', '!=', 'cancel')])

