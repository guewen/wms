# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _split_and_apply_routing(self):
        moves = super()._split_and_apply_routing()
        # When we "release" moves, we set the "printed" flag on the transfers,
        # because after a release, we shouldn't have any new move merged in a
        # "wave" of release.

        # The stock_available_to_promise_release module adds the flag on all
        # the transfer chain (pick, pack, ship, ...), but as transfers created
        # for dynamic routing are created later, they need to be handled
        # specially, which is done in this module.

        need_release_moves = self.browse()
        need_release_move_ids = self.env.context.get("_need_release_move_ids")
        if need_release_move_ids:
            # adds the "OUT" moves which have been just released
            need_release_moves |= self.browse(need_release_move_ids)
            # this will walk the from the "out" moves to the newly generated
            # moves
            need_release_moves._release_set_printed()

        moves._release_routing_set_printed()

        return moves

    def _release_routing_set_printed(self):
        picking_ids = set()
        # since the routing adds moves after the current one to reach the
        # destination, look for all the moves (and their picking) that goes to
        # a "printed" picking and set their picking to "printed"
        for move in self:
            current_picking_ids = set()
            current_moves = move
            while current_moves:
                dest_moves = current_moves.move_dest_ids
                if not dest_moves:
                    if any(picking.printed for picking in current_moves.picking_id):
                        # we have reached the last moves of the chain and they
                        # are printed, set all the chain to printed
                        picking_ids.update(current_picking_ids)
                    break
                current_picking_ids.update(current_moves.picking_id.ids)
                current_moves = dest_moves
        pickings = self.env["stock.picking"].browse(picking_ids)
        pickings.filtered(lambda p: not p.printed).printed = True

    def _run_stock_rule(self):
        need_release_moves = self.filtered("need_release")
        return super(
            StockMove, self.with_context(_need_release_move_ids=need_release_moves.ids)
        )._run_stock_rule()
