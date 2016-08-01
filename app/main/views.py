from . import main
from .forms import PO_lineForm, NewShipVia_Form, New_VendorForm, Edit_VendorForm, FileUpload_Form, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import PO_line, Vendor, Ship_via, Packing_slip, Coo, User, Role, Post, Permission
from ..email import send_email
from flask import Flask, render_template, request, session, redirect, url_for, flash, current_app, abort, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
import os

ALLOWED_EXTENSIONS = set(['txt'])

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/favicon.png')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'), 'favicon.png')

@main.route('/orders')
@permission_required(Permission.VIEW)
@login_required
def orders():
    # orders = PO_line.query.filter(PO_line.status < 5).order_by(PO_line.expected_del_date.asc()).all()
    vendors = Vendor.query.order_by(Vendor.name.asc()).all()
    ship_vias = Ship_via.query.order_by(Ship_via.name.asc()).all()
    orders = get_orders_from_session()
    pagination = orders.order_by(PO_line.expected_del_date.asc(), PO_line.po_number.asc()).paginate(session.get('page',1),per_page=current_app.config['ITEMS_PER_PAGE'],error_out=False)
    orders = pagination.items
    return render_template('orders.html', orders=orders, vendors=vendors, ship_vias=ship_vias, pagination=pagination)


@main.route('/view_orders/', methods=['GET','POST'])
@login_required
@permission_required(Permission.VIEW)
def view_orders():
    orders = get_orders_from_session()
    pagination = orders.order_by(PO_line.expected_del_date.asc(), PO_line.po_number.asc()).paginate(session.get('page',1),per_page=current_app.config['ITEMS_PER_PAGE'],error_out=False)
    orders = pagination.items
    return render_template('_view_orders.html', orders=orders, pagination=pagination)

@main.route('/update_selected_orders/<int:id>', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def update_selected_orders(id):
    po_line = PO_line.query.get_or_404(id)
    chk_edit_expected_del_date = request.form.get('chk_edit_expected_del_date')=='true'
    chk_edit_ship_via = request.form.get('chk_edit_ship_via')=='true'
    chk_edit_tracking_number = request.form.get('chk_edit_tracking_number')=='true'
    chk_edit_status = request.form.get('chk_edit_status')=='true'
    chk_edit_priority = request.form.get('chk_edit_priority')=='true'
    txt_edit_expected_del_date = request.form.get('txt_edit_expected_del_date','',type=str)
    sel_edit_ship_via = request.form.get('sel_edit_ship_via',0,type=int)
    txt_edit_tracking_number = request.form.get('txt_edit_tracking_number','',type=str)
    sel_edit_status = request.form.get('sel_edit_status',0,type=int)
    sel_edit_priority = request.form.get('sel_edit_priority',0,type=int)
    print(chk_edit_tracking_number, txt_edit_tracking_number)
    if chk_edit_expected_del_date:
        try:
            po_line.expected_del_date=datetime.strptime(txt_edit_expected_del_date,'%m/%d/%y')
        except:
            passpo_line.get_or_404(id)
    if chk_edit_ship_via and sel_edit_ship_via is not None and sel_edit_ship_via>0:
        po_line.ship_via_id = sel_edit_ship_via
    if chk_edit_tracking_number:
        po_line.tracking_number = txt_edit_tracking_number
    if chk_edit_status and sel_edit_status is not None:
        po_line.status = sel_edit_status
        if po_line.qty_received==0 and sel_edit_status>=3 and sel_edit_status <=5:
            po_line.qty_received = po_line.qty_ordered
            po_line.balance = 0
    if chk_edit_priority and sel_edit_priority is not None:
        po_line.priority= sel_edit_priority==1
    db.session.add(po_line)
    db.session.commit()
    return "Ok"

@main.route('/view_shipvias/')
@login_required
@permission_required(Permission.VIEW)
def view_shipvias():
    ship_vias = Ship_via.query.all()
    return render_template('ship_vias.html', ship_vias=ship_vias)

@main.route('/view_vendors/')
@login_required
@permission_required(Permission.VIEW)
def view_vendors():
    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@main.route('/edit_ship_via/<int:id>', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def edit_ship_via(id):
    ship_via = Ship_via.query.get_or_404(id)
    form = NewShipVia_Form()
    if form.validate_on_submit():
        if form.code.data != ship_via.code:
            s = Ship_via.query.filter_by(code=form.code.data).first()
            if s is not None:
                flash("Ship via code '{}' is already registered.".format(form.code.data))
        else:
            ship_via.code =form.code.data
            ship_via.name = form.name.data
            ship_via.tracking_url = form.tracking_url.data
            db.session.add(ship_via)
            db.session.commit()
            flash ("Ship via '{}' has been updated.".format(form.name.data))
        ship_vias = Ship_via.query.all()
        return render_template('ship_vias.html', ship_vias=ship_vias)
    else:
        form.code.data = ship_via.code
        form.name.data = ship_via.name
        form.tracking_url.data = ship_via.tracking_url
        return render_template('edit_ship_via.html',form=form)

@main.route('/edit_vendor/<int:id>', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    form = Edit_VendorForm(vendor=vendor)
    if form.validate_on_submit():
        vendor.vendor_number = form.vendor_number.data
        vendor.name = form.name.data
        vendor.contact = form.contact.data
        vendor.email = form.email.data
        vendor.website = form.website.data
        vendor.phone = form.phone.data
        vendor.default_ship_via_id = form.default_ship_via_id.data
        db.session.add(vendor)
        db.session.commit()
        flash("Vendor '{}' has been updated.".format(vendor.name))
        vendors = Vendor.query.all()
        return render_template('vendors.html', vendors=vendors)
    else:
        form.vendor_number.data = vendor.vendor_number
        form.name.data = vendor.name
        form.contact.data = vendor.contact
        form.email.data = vendor.email
        form.website.data = vendor.website
        form.phone.data = vendor.phone
        form.default_ship_via_id.data = vendor.default_ship_via_id
        return render_template('edit_vendor.html', form=form)

@main.route('/new_shipvia/', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def new_shipvia():
    form = NewShipVia_Form()
    if form.validate_on_submit():
        s = Ship_via.query.filter_by(code=form.code.data).first()
        if s is None:
            s = Ship_via(code=form.code.data, name=form.name.data, tracking_url=form.tracking_url.data)
            db.session.add(s)
            db.session.commit()
            flash('{} has been registered.'.format(form.name.data))
            return redirect(url_for('.orders'))
        else:
            flash('Ship via: {} was already registered.'.format(form.code.data))
            return redirect(url_for('.view_shipvias'))
    else:
        return render_template('new_shipvia.html',form=form)


@main.route('/new_vendor/', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def new_vendor():
    form = New_VendorForm()
    if form.validate_on_submit():
        v = Vendor(vendor_number=form.vendor_number.data, name=form.name.data, contact=form.contact.data, email=form.email.data, website=form.website.data, phone=form.phone.data, default_ship_via_id=form.default_ship_via_id.data)
        db.session.add(v)
        db.session.commit()
        flash("Vendor '{}' has been saved.".format(v.name))
        return redirect(url_for('.view_vendors'))
    else:
        return render_template('new_vendor.html',form=form)


@main.route('/order/<int:id>', methods=['GET','POST'])
@login_required
@permission_required(Permission.MODIFY)
def order(id):
    po_line = PO_line.query.get_or_404(id)
    form = PO_lineForm(po_line=po_line)
    if form.validate_on_submit():
        po_line.qty_received = form.qty_received.data
        if po_line.qty_received > po_line.qty_ordered:
            po_line.qty_ordered = po_line.qty_received
        po_line.balance = po_line.qty_ordered-po_line.qty_received
        po_line.expected_del_date = form.expected_del_date.data
        print("Date: " , form.expected_del_date.data)
        po_line.ship_via_id = form.ship_via.data
        po_line.tracking_number = form.tracking_number.data
        po_line.status = form.status.data
        if po_line.status >=3 and po_line.status <=5 and po_line.qty_received == 0:
            po_line.qty_received = po_line.qty_ordered
            po_line.balance = 0
        po_line.priority = form.priority.data
        print(form.apply_to_all_order.data)
        if form.apply_to_all_order.data:
            print(po_line.po_number[:6])
            items = PO_line.query.filter(PO_line.po_number.like(po_line.po_number[:6]+'%')).all()
            for i in items:
                print(i.po_number)
                i.expected_del_date= form.expected_del_date.data
                i.status = form.status.data
                if i.qty_received ==0 and i.status >=3 and i.status <=5:
                    i.qty_received = i.qty_ordered
                    i.balance = 0
                i.ship_via_id = form.ship_via.data
                i.tracking_number = form.tracking_number.data
                i.priority = form.priority.data
                db.session.add(i)
            db.session.commit()
            flash('All the items on PO# {} have been updated.'.format(po_line.po_number[:6]))
        else:
            db.session.add(po_line)
            db.session.commit()
            flash('Order# %s has been updated.' % po_line.po_number)
        return redirect(url_for('.orders'))
    form.qty_received.data = po_line.qty_received
    form.expected_del_date.data = po_line.expected_del_date
    form.ship_via.data = po_line.ship_via_id
    form.tracking_number.data = po_line.tracking_number
    form.status.data = po_line.status
    form.priority.data = po_line.priority
    return render_template('order.html',form=form, po_line=po_line)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.position = form.position.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user',username=current_user.username))
    form.name.data = current_user.name
    form.position.data = current_user.position
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.position = form.position.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.position.data = user.position
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/subscribe/<int:id>', methods=['POST'])
@login_required
@permission_required(Permission.SUBSCRIBE)
def subscribe(id):
    po_line = PO_line.query.get_or_404(id)
    current_user.follow(po_line)
    return 'subscribed'

@main.route('/unsubscribe/<int:id>', methods=['GET','POST'])
@login_required
@permission_required(Permission.SUBSCRIBE)
def unsubscribe(id):
    po_line = PO_line.query.get_or_404(id)
    current_user.unfollow(po_line)
    return 'unsubscribed'

@main.route('/order_details/<int:id>', methods=['POST'])
@login_required
@permission_required(Permission.VIEW)
def order_details(id):
    po_line = PO_line.query.get_or_404(id)
    posts = Post.query.filter_by(po_line_id=id).order_by(Post.timestamp.desc()).all()
    return render_template('_order_details.html',po_line=po_line, posts=posts)

@main.route('/post_comment/<int:id>', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def post_comment(id):
    po_line = PO_line.query.get_or_404(id)
    comment = request.form.get('comment',"",type=str)
    if comment and comment!="":
        post = Post(body=comment, author_id=current_user.id, po_line_id=id)
        db.session.add(post)
        db.session.commit()
    return "Ok"


@main.route('/import/', methods=['GET','POST'])
@login_required
@admin_required
def import_file():
    form =FileUpload_Form()
    if form.validate_on_submit():
        if 'fileUpload' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['fileUpload']
        if file.filename == '':
            flash('No selected file.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            import_data(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('.orders'))
    return render_template('import.html', form=form)

@main.route('/refresh_pagination/', methods=['GET','POST'])
@login_required
def refresh_pagination():
    return render_template('_refresh_pagination.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def import_data(filename):
    import re
    r = re.compile('.+A[0-9]{5}')
    ship_via_na = Ship_via.query.filter_by(code='NA').first()
    with open(filename)as f:
        for line in f:
            mo = r.match(line)
            if mo is not None:
                pn = line[0:20].strip()
                if len(pn)>3 and pn[-3:]=='|41':
                    pn=pn[:-3]
                    inv_type = "I"
                else:
                    inv_type = "N"
                po_number = line[20:34].strip()
                po_date=datetime.strptime(line[34:43].strip(),'%m-%d-%y')
                buyer = line[43:46].strip()
                vendor_number=int(line[46:53].strip())
                description = line[53:72].strip()
                expected_del_date = datetime.strptime(line[72:81].strip(),'%m-%d-%y')
                qty_ordered = get_qty(line[81:89].strip())
                qty_received = get_qty(line[89:97].strip())
                balance = get_qty(line[97:106].strip())
                if balance == 1 and vendor_number ==12612:
                    continue    #skip blanket order helpers.
                p = PO_line.query.filter_by(po_number=po_number).first()
                if p is not None:
                    p.expected_del_date = expected_del_date
                    p.qty_ordered = qty_ordered
                    p.qty_received = qty_received
                    p.balance = balance
                    db.session.add(p)
                else:
                    v = Vendor.query.filter_by(vendor_number=vendor_number).first()
                    if v is None:
                        flash("Vendor# {} is not registered. Please insert this vendor before importing.".format(vendor_number))
                        return
                    p = PO_line(po_number=po_number, pn=pn, po_date=po_date, buyer=buyer, vendor_id=v.id, description=description, expected_del_date=expected_del_date, qty_ordered=qty_ordered, qty_received=qty_received, balance=balance, ship_via_id=v.default_ship_via_id,status=0,tracking_number='', inv_type=inv_type)
                    db.session.add(p)
    db.session.commit()
    flash('File has been imported.')

def get_qty(s):
    if s == '':
        return 0
    else:
        return int(s.strip().replace(',',''))

def get_orders_from_session():
    status=request.form.get('status',None,type=int)
    if status is not None:
        session['status']=status

    chk_status = request.form.get('chk_status',None)
    if chk_status:
        session['chk_status']=chk_status=='true'

    chk_vendor = request.form.get('chk_vendor',None)
    if chk_vendor:
        session['chk_vendor']=chk_vendor=='true'

    chk_inv_type = request.form.get('chk_inv_type',None)
    if chk_inv_type:
        session['chk_inv_type']=chk_inv_type=='true'

    chk_pn = request.form.get('chk_pn',None)
    if chk_pn:
        session['chk_pn']=chk_pn=='true'

    chk_po = request.form.get('chk_po',None)
    if chk_po:
        session['chk_po']=chk_po=='true'

    chk_expected_del_date = request.form.get('chk_expected_del_date',None)
    if chk_expected_del_date:
        session['chk_expected_del_date']=chk_expected_del_date=='true'

    sel_vendor = request.form.get('sel_vendor',None,type=int)
    if sel_vendor:
        session['sel_vendor']=sel_vendor

    sel_inv_type = request.form.get('sel_inv_type',None,type=int)
    if sel_inv_type:
        session['sel_inv_type']=sel_inv_type

    txt_pn = request.form.get('txt_pn',None,type=str)
    if txt_pn:
        session['txt_pn']=txt_pn.upper().replace(' ','')

    txt_po = request.form.get('txt_po',None,type=str)
    if txt_po:
        session['txt_po']=txt_po.upper().replace(' ','')

    txt_expected_del_date = request.form.get('txt_expected_del_date',None,type=str)
    if txt_expected_del_date:
        session['txt_expected_del_date']=txt_expected_del_date
    # print("chk_status: {}\n chk_vendor: {}\n chk_pn: {}\n chk_po: {}\n chk_inv_type: {}\n chk_expected_del_date: {}".format(session['chk_status'], session['chk_vendor'], session['chk_pn'], session['chk_po'], session['chk_inv_type'], session['chk_expected_del_date']))
    # print("status: {}\n sel_vendor: {}\n txt_pn: {}\n txt_po: {}\n sel_inv_type: {}\n txt_expected_del_date: {}".format(session['status'], session['sel_vendor'], session['txt_pn'], session['txt_po'], session['sel_inv_type'], session['txt_expected_del_date']))
    orders = PO_line.query

    if session.get('chk_status') and session.get('status') is not None and session.get('status') <8:
        orders = orders.filter_by(status=session['status'])
    elif session.get('chk_status') and session.get('status') and session['status']==8:
        orders = orders.filter(PO_line.status < 3)
    else:
        orders = orders.filter(PO_line.status < 5)

    if session.get('chk_vendor') and session['sel_vendor'] is not None and session.get('sel_vendor') !=1000 :
        orders = orders.filter_by(vendor_id=session['sel_vendor'])

    if session.get('chk_inv_type') and session['sel_inv_type'] is not None:
        if session['sel_inv_type']==1:
            orders = orders.filter_by(inv_type='I')
        else:
            orders = orders.filter_by(inv_type='N')

    if session.get('chk_pn') and session.get('txt_pn') is not None and session['txt_pn']!='':
        orders = orders.filter(PO_line.pn.like(session['txt_pn'].upper().replace(' ','')+'%'))

    if session.get('chk_po') and session.get('txt_po') is not None and session['txt_po']!='':
        orders = orders.filter(PO_line.po_number.like(session['txt_po'].upper()+'%'))

    if session.get('chk_expected_del_date'):
        try:
            d = datetime.strptime(session.get('txt_expected_del_date'),'%m/%d/%y')
            orders = orders.filter_by(expected_del_date=d)
        except:
            pass

    page = request.args.get('page')
    if page is not None:
        session['page']=int(page)
    else:
        session['page']=1

    return orders
