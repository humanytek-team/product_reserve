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
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
import logging
_logger = logging.getLogger(__name__)


class Reserve(models.TransientModel):
    _name = "reserve"

    qty_reserve = fields.Float('Quantity', required=True)
    stock_move_out_id = fields.Many2one('stock.move', 'Outgoing products',
            default=lambda self: self._context.get('move_out'), required=True)

    @api.multi
    def confirm(self):
        move = self.stock_move_out_id
        move.action_assign_qty(self.qty_reserve, self._context.get('compromise'))

