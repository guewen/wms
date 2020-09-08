from odoo import fields, models


class StockPackageLevel(models.Model):
    _inherit = "stock.package_level"

    shopfloor_postponed = fields.Boolean(
        default=False,
        copy=False,
        help="Technical field. "
        "Indicates if a the package level has been postponed in a barcode scenario.",
    )

    def replace_package(self, new_package):
        """Replace a package on an assigned package level and related records

        The replacement package must have the same properties (same products
        and quantities).
        """
        if self.state not in ("new", "assigned"):
            return

        move_lines = self.move_line_ids
        # the write method on stock.move.line updates the reservation on quants
        move_lines.package_id = new_package
        # when a package is set on a line, the destination package is the same
        # by default
        move_lines.result_package_id = new_package
        for quant in new_package.quant_ids:
            for line in move_lines:
                if line.product_id == quant.product_id:
                    line.lot_id = quant.lot_id
                    line.owner_id = quant.owner_id

        self.package_id = new_package

    def shallow_unlink(self):
        """Unlink package level without affecting moves and lines"""
        if not self:
            return True
        # when we unlink a package level, it automatically drops
        # any related move and resets the result_package_id of
        # move lines, we prevent this by detaching it first
        self.write({"move_ids": [(6, 0, [])], "move_line_ids": [(6, 0, [])]})
        # as we are no longer moving an entire package, the
        # package level is irrelevant
        return self.unlink()
