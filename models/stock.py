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

from odoo import api, models
from odoo.tools.float_utils import float_compare
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = 'stock.move'

    @api.one
    def action_done(self):
        if super(StockMove, self).action_done():
            StockQuant = self.env['stock.quant']
            ProductCompromise = self.env['product.compromise']
            product_compromises = ProductCompromise.search([
                                    ('stock_move_in_id.id', '=', self.id)])
            for product_compromise in product_compromises:
                move = product_compromise.stock_move_out_id
                move_in = product_compromise.stock_move_in_id
                if move_in.quant_ids:
                    quant = move_in.quant_ids[len(move_in.quant_ids) - 1]
                    quants = [(quant, product_compromise.qty_compromise)]
                    StockQuant.quants_reserve(quants, move)
        return True

    @api.multi
    def action_reserve(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reserve',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'compromise': self.compromise_qty,
                        'move_out': self.id,
                        'qty': self.product_uom_qty},
            'views': [(False, 'form')],
            'target': 'new',
            }

    @api.multi
    def action_assign_qty(self, qty_reserve=0, qty_compromise=0):
        """ Checks the product type and accordingly writes the state. """
        # TDE FIXME: remove decorator once everything is migrated
        # TDE FIXME: clean me, please
        main_domain = {}

        Quant = self.env['stock.quant']
        moves_to_assign = self.env['stock.move']
        moves_to_do = self.env['stock.move']
        operations = self.env['stock.pack.operation']
        ancestors_list = {}

        # work only on in progress moves
        moves = self.filtered(lambda move: move.state in ['confirmed', 'waiting', 'assigned'])
        moves.filtered(lambda move: move.reserved_quant_ids).do_unreserve()
        for move in moves:
            if move.location_id.usage in ('supplier', 'inventory', 'production'):
                moves_to_assign |= move
                # TDE FIXME: what ?
                # in case the move is returned, we want to try to find quants before forcing the assignment
                if not move.origin_returned_move_id:
                    continue
            # if the move is preceeded, restrict the choice of quants in the ones moved previously in original move
            ancestors = move.find_move_ancestors()
            if move.product_id.type == 'consu' and not ancestors:
                moves_to_assign |= move
                continue
            else:
                moves_to_do |= move

                # we always search for yet unassigned quants
                main_domain[move.id] = [('reservation_id', '=', False), ('qty', '>', 0)]

                ancestors_list[move.id] = True if ancestors else False
                if move.state == 'waiting' and not ancestors:
                    # if the waiting move hasn't yet any ancestor (PO/MO not confirmed yet), don't find any quant available in stock
                    main_domain[move.id] += [('id', '=', False)]
                elif ancestors:
                    main_domain[move.id] += [('history_ids', 'in', ancestors.ids)]

                # if the move is returned from another, restrict the choice of quants to the ones that follow the returned move
                if move.origin_returned_move_id:
                    main_domain[move.id] += [('history_ids', 'in', move.origin_returned_move_id.id)]
                for link in move.linked_move_operation_ids:
                    operations |= link.operation_id

        # Check all ops and sort them: we want to process first the packages, then operations with lot then the rest
        #operations = operations.sorted(key=lambda x: ((x.package_id and not x.product_id) and -4 or 0) + (x.package_id and -2 or 0) + (x.pack_lot_ids and -1 or 0))
        #_logger.info('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        #_logger.info(operations)
        #for ops in operations:
            ## TDE FIXME: this code seems to be in action_done, isn't it ?
            ## first try to find quants based on specific domains given by linked operations for the case where we want to rereserve according to existing pack operations
            ##if not (ops.product_id and ops.pack_lot_ids):
                ##for record in ops.linked_move_operation_ids:
                    ##move = record.move_id
                    ##if move.id in main_domain:
                        ##qty = record.qty
                        ##domain = main_domain[move.id]
                        ##if qty:
                            ##quants = Quant.quants_get_preferred_domain(qty, move, ops=ops, domain=domain, preferred_domain_list=[])
                            ##Quant.quants_reserve(quants, move, record)
            ##else:
            #if (ops.product_id and ops.pack_lot_ids):
                #lot_qty = {}
                #rounding = ops.product_id.uom_id.rounding
                #for pack_lot in ops.pack_lot_ids:
                    #lot_qty[pack_lot.lot_id.id] = ops.product_uom_id._compute_quantity(pack_lot.qty, ops.product_id.uom_id)
                #for record in ops.linked_move_operation_ids:
                    #move_qty = record.qty - qty_compromise
                    #move = record.move_id
                    #domain = main_domain[move.id]
                    #for lot in lot_qty:
                        #if float_compare(lot_qty[lot], 0, precision_rounding=rounding) > 0 and float_compare(move_qty, 0, precision_rounding=rounding) > 0:
                            #qty = min(lot_qty[lot], move_qty)
                            #quants = Quant.quants_get_preferred_domain(qty, move, ops=ops, lot_id=lot, domain=domain, preferred_domain_list=[])
                            #Quant.quants_reserve(quants, move, record)
                            #lot_qty[lot] -= qty
                            #move_qty -= qty

        ## Sort moves to reserve first the ones with ancestors, in case the same product is listed in
        ## different stock moves.
        for move in sorted(moves_to_do, key=lambda x: -1 if ancestors_list.get(x.id) else 0):
            # then if the move isn't totally assigned, try to find quants without any specific domain
            if move.state != 'assigned' and not self.env.context.get('reserve_only_ops'):
                qty_already_assigned = move.reserved_availability

                qty = move.product_qty - qty_already_assigned - qty_compromise
                qty = min(qty, qty_reserve)

                quants = Quant.quants_get_preferred_domain(qty, move, domain=main_domain[move.id], preferred_domain_list=[])
                Quant.quants_reserve(quants, move)

        # force assignation of consumable products and incoming from supplier/inventory/production
        # Do not take force_assign as it would create pack operations
        if moves_to_assign:
            moves_to_assign.write({'state': 'assigned'})
        self.check_move_lots()