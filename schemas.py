from marshmallow import Schema, fields

# Define plain schemas for nesting. Only include a part
# of the fields, and not the nested fields.
class PlainItemSchema(Schema):

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)


class ItemUpdateSchema(Schema):

    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()

# [!] Nested fields.
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema, dump_only=True)


class StoresSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)