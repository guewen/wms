# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    location_storage_type_ids = fields.Many2many(
        "stock.location.storage.type",
        "stock_location_location_storage_type_rel",
        "location_id",
        "location_storage_type_id",
        help="Location storage types defined here will be applied on all the "
        "children locations that do not define their own location "
        "storage types.",
    )

    allowed_location_storage_type_ids = fields.Many2many(
        "stock.location.storage.type",
        "stock_location_allowed_location_storage_type_rel",
        "location_id",
        "location_storage_type_id",
        compute="_compute_allowed_location_storage_type_ids",
        store=True,
        help="Locations storage types that this location can accept. (If no "
        "location storage types are defined on this specific location, "
        "the location storage types of the parent location are applied).",
    )

    @api.depends(
        "location_storage_type_ids", "location_id.location_storage_type_ids"
    )
    def _compute_allowed_location_storage_type_ids(self):
        for location in self:
            current_types = location.allowed_location_storage_type_ids
            if (
                location.location_storage_type_ids
                and location.location_storage_type_ids != current_types
            ):
                location.allowed_location_storage_type_ids = (
                    location.location_storage_type_ids
                )
            else:
                parent = location.location_id
                while parent:
                    if (
                        parent.location_storage_type_ids
                        and parent.location_storage_type_ids != current_types
                    ):
                        location.allowed_location_storage_type_ids = (
                            parent.location_storage_type_ids
                        )
                        break
                    parent = parent.location_id
