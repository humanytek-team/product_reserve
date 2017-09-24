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


class ProductCompromise(models.Model):
    _name = "product.compromise"

    qty_compromise = fields.Float('Compromise quantity')
    stock_move_in_id = fields.Many2one('stock.move', 'Incoming products')
    stock_move_out_id = fields.Many2one('stock.move', 'Outgoing products')
    state = fields.Selection(related='stock_move_in_id.state',
                              string='State', readonly=True, store=False)
    product_id = fields.Many2one(related='stock_move_in_id.product_id',
                              string='Product', readonly=True, store=False)
    move_picking_id = fields.Many2one(related='stock_move_in_id.picking_id',
                              string='', readonly=True, store=False)

    _sql_constraints = [
        ('stock_move_uniq',
         'UNIQUE (stock_move_in_id, stock_move_out_id)',
         'the relationship must be unique!')]