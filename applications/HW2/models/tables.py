# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

db.define_table('products',
                Field('name'),
                Field('descr',  label='Description'),
                Field('stock', 'integer', requires=IS_INT_IN_RANGE(0)),
                Field('sold', 'integer', requires=IS_INT_IN_RANGE(0)),
                Field('price', 'float', requires=IS_FLOAT_IN_RANGE(0)),
                Field('cost_p', 'float', label='Cost', requires=IS_FLOAT_IN_RANGE(0)),
                Field('star', 'boolean'),
                Field('user_id'),
                )
db.products.profit = Field.Virtual(lambda row: round(((row.products.price - row.products.cost_p) * row.products.sold), 2))
db.products.profit.label = 'Profit'
db.products.profit.type = 'float'
# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
