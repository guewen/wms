from .common import CommonCase


class TestStockMoveLineChangeResultPackage(CommonCase):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super().setUpClassVars(*args, **kwargs)
        cls.wh = cls.env.ref("stock.warehouse0")

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super().setUpClassBaseData(*args, **kwargs)
        cls.wh.sudo().delivery_steps = "pick_pack_ship"

        cls.package = cls.env["stock.quant.package"].create({})
        cls.dest_package1 = cls.env["stock.quant.package"].create({})
        cls.dest_package2 = cls.env["stock.quant.package"].create({})

        cls.picking = picking = cls._create_picking(
            picking_type=cls.wh.pick_type_id, lines=[(cls.product_a, 50)]
        )
        cls._fill_stock_for_moves(picking.move_lines, in_package=cls.package)
        picking.action_assign()

        cls.line1 = picking.move_line_ids
        cls.line2 = cls.line1.copy({"product_uom_qty": 8})
        cls.line3 = cls.line1.copy({"product_uom_qty": 12})
        cls.line1.with_context(bypass_reservation_update=True).product_uom_qty = 30

    def test_change_result_package_rm_package_level(self):
        """Package level is deleted when we change the result package

        But the previously result package set on the line is kept.
        """
        # on line 1, we leave the original package
        # on line 2, we set another result package
        self.line2.result_package_id = self.dest_package1
        self.assertFalse(self.picking.package_level_ids)
        self.assertFalse(self.line1.result_package_id)
        self.assertEqual(self.line2.result_package_id, self.dest_package1)
        self.assertFalse(self.line3.result_package_id)

        self.line3.result_package_id = self.dest_package2
        self.assertFalse(self.line1.result_package_id)
        self.assertEqual(self.line2.result_package_id, self.dest_package1)
        self.assertEqual(self.line3.result_package_id, self.dest_package2)
