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

    @api.multi
    def action_done(self):
        if super(StockMove, self).action_done():
            StockQuant = self.env['stock.quant']
            ProductCompromise = self.env['product.compromise']
            product_compromises = ProductCompromise.search([('stock_move_in_id',
                                                    '=', self.id)])
            for product_compromise in product_compromises:
                move = product_compromise.stock_move_out_id
                move_in = product_compromise.stock_move_in_id
                if move_in.quant_ids:
                    quant = move_in.quant_ids[len(move_in.quant_ids) - 1]
                    quants = [(quant, product_compromise.qty_compromise)]
                    StockQuant.quants_reserve(quants, move)

        return True