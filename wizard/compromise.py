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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Compromise(models.TransientModel):
    _name = "compromise"

    qty_compromise = fields.Float('Compromise quantity', required=True)
    stock_move_in_id = fields.Many2one('stock.move', 'Incoming products',
        domain=lambda self: [
            ('product_id.id', '=', self._context.get('product_id')),
            ('picking_type_id.code', '=', 'incoming'),
            ('state', '=', 'assigned')], required=True)
    stock_move_out_id = fields.Many2one('stock.move', 'Outgoing products',
            default=lambda self: self._context.get('move_out'), required=True)

    @api.multi
    def confirm(self):
        ProductCompromise = self.env['product.compromise']
        product_compromises = ProductCompromise.search([
                            ('stock_move_out_id.id', '=', self.stock_move_out_id.id),
                            ('state', '=', 'assigned')])
        compromise = sum([product_compromise.qty_compromise
                                for product_compromise in
                                product_compromises])
        product_in_compromises = ProductCompromise.search([
                            ('stock_move_in_id.id', '=', self.stock_move_in_id.id)
                            ])
        compromise_in = sum([product_in_compromise.qty_compromise
                                for product_in_compromise in
                                product_in_compromises])
        if (self._context.get('qty') - self.stock_move_out_id.reserved_availability - compromise) < self.qty_compromise:
            raise ValidationError(
                    _('the quantity of products must be less than the quantity of products in the movement'))
        elif (self.qty_compromise > self.stock_move_in_id.product_uom_qty - compromise_in):
            raise ValidationError(
                    _('the quantity of products must be less than the quantity of incoming products'))
        else:
            ProductCompromise.create({
                                'qty_compromise': self.qty_compromise,
                                'stock_move_in_id': self.stock_move_in_id.id,
                                'stock_move_out_id': self.stock_move_out_id.id})


class Liberate(models.TransientModel):
    _name = "liberate"

    stock_move_in_id = fields.Many2one('stock.move', 'Incoming',
        domain=lambda self: [
            ('id', 'in', self._context.get('lista')),
            ('state', '!=', 'done')])

    @api.multi
    def confirm(self):
        product_compromise_obj = self.env['product.compromise']
        product_compromise = product_compromise_obj.search([
            ('stock_move_in_id', '=', self.stock_move_in_id.id),
            ('stock_move_out_id', '=', self._context.get('move_out'))])
        product_compromise.unlink()