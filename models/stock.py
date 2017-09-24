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
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = 'stock.move'

    product_compromise_ids = fields.One2many('product.compromise',
                            'stock_move_out_id',
                            'Compromise Products')

    compromise_qty = fields.Float('Compromise',
                            compute='_compute_compromise_qty', readonly=True)

    product_qty_product = fields.Float(related='product_id.qty_available',
                            string='Total Product', readonly=True, store=False)

    product_incoming_qty = fields.Float(related='product_id.incoming_qty',
                            string='Total Incoming Product', readonly=True,
                            store=False)

    total_compromise_product = fields.Float('Total Compromise Product',
                            compute='_compute_total_compromise_product',
                            readonly=True, store=False)

    total_reserved_product = fields.Float('Total Reserved Product',
                            compute='_compute_total_reserved_product',
                            readonly=True, store=False)

    @api.multi
    def _compute_compromise_qty(self):
        self.compromise_qty = sum([product_compromise.qty_compromise
                                for product_compromise in
                                self.product_compromise_ids
                                if product_compromise.state == 'assigned'])

    @api.one
    def _compute_total_compromise_product(self):
        ProductCompromise = self.env['product.compromise']
        product_compromises = ProductCompromise.search([
                                    ('product_id.id', '=', self.product_id.id),
                                    ('state', '=', 'assigned')])

        self.total_compromise_product = sum([product_compromise.qty_compromise
                                for product_compromise in
                                product_compromises])

    @api.one
    def _compute_total_reserved_product(self):
        StockMove = self.env['stock.move']
        stock_moves = StockMove.search([
                                    ('product_id.id', '=', self.product_id.id),
                                    ('state', 'in', ('assigned', 'confirmed'))])
        self.total_reserved_product = sum([stock_move.reserved_availability
                                for stock_move in
                                stock_moves])

    @api.multi
    def action_compromise(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'compromise',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'product_id': self.product_id.id,
                        'move_out': self.id,
                        'qty': self.product_uom_qty},
            'views': [(False, 'form')],
            'target': 'new',
            }

    @api.multi
    def action_liberate(self):
        lista = []
        for product_compromise in self.product_compromise_ids:
            lista.append(product_compromise.stock_move_in_id.id)
            _logger.info(lista)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'liberate',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'product_id': self.product_id.id,
                        'move_out': self.id,
                        'lista': lista},
            'views': [(False, 'form')],
            'target': 'new',
            }

    @api.multi
    def action_cancel(self):
        if super(StockMove, self).action_cancel():
            ProductCompromise = self.env['product.compromise']
            product_compromises = ProductCompromise.search([
                                ('stock_move_out_id.state', '=', 'cancel')])
            product_compromises.unlink()