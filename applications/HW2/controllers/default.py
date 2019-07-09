# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    rows = db(db.products).select()
    return dict(
        rows=rows,
    )

@auth.requires_login()
def create():
    form = SQLFORM.factory(
        Field('name', label='Name'),
        Field('descr', label='Description'),
        Field('stock', label='Quantity in Stock', type='integer', requires=IS_INT_IN_RANGE(0)),
        Field('price', label='Sales Price', type='float', requires=IS_FLOAT_IN_RANGE(0)),
        Field('cost_p', label='Cost', type='float', requires=IS_FLOAT_IN_RANGE(0)),
    )
    # We can process the form.  This will check that the request is a PRODUCTS,
    # and also perform validation, but in this case there is no validation.
    if form.process().accepted:
        # We insert the result.
        db.products.insert(
            name=form.vars.name,
            descr=form.vars.descr,
            stock=form.vars.stock,
            price=form.vars.price,
            cost_p=form.vars.cost_p,
            star=False,
            sold=0,
            user_id=auth.user.email
        )
        # And we load default/viewall via redirect.
        redirect(URL('default', 'viewall'))
    # We ask web2py to lay out the form for us.
    logger.info("My session is: %r" % session)
    return dict(form=form)

def viewall():
    """This controller uses a grid to display all products."""
    links = []
    if auth.user is not None:
        links.append(
            dict(header='',
                 body=lambda row:
                 (A(I(_class='fa fa-star'), _style="color:gold;",
                    _href=URL('default', 'star', args=[row.id], user_signature=True)))
                 if db.products(row.id).star
                 else
                 (A(I(_class='fa fa-star-o'), _style="color:black;",
                    _href=URL('default', 'star', args=[row.id], user_signature=True)))
                 )
        )

        links.append(
            dict(header='',
                 body=lambda row:
                 SPAN(A('-',
                        _href=URL('default', 'sub_stock', args=[row.id], user_signature=True),
                        _class='btn'),
                      _class="haha")
                 if db.products(row.id).stock != 0
                 else
                 SPAN(A('-',
                        _class='btn', _style="background:grey;"),
                      _class="haha")
                 )
        )
        links.append(
            dict(header='',
                 body=lambda row:
                 SPAN(A('+',
                        _href=URL('default', 'add_stock', args=[row.id], user_signature=True),
                        _class='btn'),
                      _class="haha")
                 )
        )

        links.append(
            dict(header='',
                 body=lambda row:
                    SPAN()
                 if db.products(row.id).user_id != auth.user.email
                 else
                     SPAN(A('Edit',
                            _href=URL('default', 'edit', args=[row.id], user_signature=True),
                            _class='btn'),
                          _class="haha")
                 )
        )

        links.append(
            dict(header='',
                 body=lambda row:
                    SPAN()
                 if db.products(row.id).user_id != auth.user.email
                 else
                     SPAN(A('Delete',
                            _href=URL('default', 'delete', args=[row.id], user_signature=True),
                            _class='btn'),
                          _class="haha")
                 )
        )
    else:
        links.append(
            dict(header='',
                 body=lambda row:
                 (A(I(_class='fa fa-star-o'), _style="color:black;"))
                 )
        )
    # Define the query separately.
    query = db.products

    # Grid definition.
    grid = SQLFORM.grid(
        query,
        field_id = db.products.id,
        fields = [db.products.name, db.products.stock, db.products.sold, db.products.price, db.products.cost_p,
                  db.products.profit],
        # And now some generic defaults.
        details=False,
        create=False, editable=False, deletable=False,
        csv=False,
        links=links,
        sortable=True,
        user_signature=True, # We don't need it as one cannot take actions directly from the form.
    )
    return dict(grid=grid)

# We require login.
@auth.requires_login()
def sub_stock():
    products = db.products(request.args(0))
    # We must validate everything we receive.
    if products is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'viewall'))
    # Decrement stock, increment sold
    products.stock -= 1
    products.sold += 1
    # Update record and redirect to default/viewall
    products.update_record()
    redirect(URL('default', 'viewall'))

# We require login.
@auth.requires_login()
def add_stock():
    products = db.products(request.args(0))
    # We must validate everything we receive.
    if products is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'viewall'))
    # Increment stock
    products.stock += 1
    # Update record and redirect to default/viewall
    products.update_record()
    redirect(URL('default', 'viewall'))

# We require login.
@auth.requires_login()
def edit():
    """Allows editing of a products.  URL form: /default/edit/<n> where n is the products id."""
    products = db.products(request.args(0))

    # Some of the product info we do not want readable or writable
    db.products.id.writable = db.products.id.readable = False
    db.products.profit.writable = db.products.profit.readable = False
    db.products.user_id.writable = db.products.user_id.readable = False
    db.products.star.writable = db.products.star.readable = False
    db.products.sold.writable = db.products.sold.readable = False

    # We must validate everything we receive.
    if products is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'viewall'))
    # One can edit only one's own products.
    if products.user_id != auth.user.email:
        logging.info("Attempt to edit some one else's products by: %r" % auth.user.email)
        redirect(URL('default', 'viewall'))
    # Now we must generate a form that allows editing the products.
    form = SQLFORM(db.products, record=products)
    if form.process().accepted:
        # The deed is done.
        redirect(URL('default', 'viewall'))
    return dict(form=form)

# We require login and a signature.
@auth.requires_signature()
@auth.requires_login()
def delete():
    products = db.products(request.args(0))
    # We must validate everything we receive.
    if products is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'viewall'))
    # One can edit only one's own posts.
    if products.user_id != auth.user.email:
        logging.info("Attempt to edit some one else's products by: %r" % auth.user.email)
        redirect(URL('default', 'viewall'))
    db(db.products.id == products.id).delete()
    redirect(URL('default', 'viewall'))

# We require login.
@auth.requires_login()
def star():
    products = db.products(request.args(0))
    # We must validate everything we receive.
    if products is None:
        logging.info("Invalid edit call")
        redirect(URL('default', 'viewall'))
    # If star is True becomes False and vice versa
    products.star = not products.star
    # Update record and redirect to default/viewall
    products.update_record()
    redirect(URL('default', 'viewall'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


