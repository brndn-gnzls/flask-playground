from marshmallow import Schema, fields


# Define plain schemas for nesting. Only include a part
# of the fields, and not the nested fields.
class PlainItemSchema(Schema):

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class ItemUpdateSchema(Schema):

    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()


# [!] Nested fields.
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema, dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class StoresSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    # {{url}}/store/1/tag
    #
    # [
    #     {
    #         "id": 1,
    #         "name": "furniture",
    #         "store": {
    #             "id": 1,
    #             "name": "my_store"
    #         }
    #     }
    # ]
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema, dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)

class UserSchema(Schema):
    id = fields.Int(dump_only=True) # since we never receive an id from the client
    username = fields.Str(required=True)
    # if load_only=False then when you return a user object
    # the password will be included in the response.
    password = fields.Str(required=True, load_only=True) # ensures the password is never sent to the client