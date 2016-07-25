from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

from flask_wtf import Form
from wtforms.fields.html5 import DateField
from wtforms import StringField, IntegerField, SubmitField, BooleanField, TextAreaField, SelectField, FileField
from flask_admin.form.widgets import DatePickerWidget
from wtforms.validators import Required, NumberRange, Optional, Email, URL, Length
from flask_sqlalchemy import SQLAlchemy
from flask_script import Shell
from flask_migrate import Migrate, MigrateCommand
# from flask_mail import Mail, Message
# from werkzeug.utils import secure_filename
# from threading import Thread
# from forms import NameForm
#
# import os
#
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# app = Flask(__name__)
# app.config['SECRET_KEY']='Winter is coming'
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir, 'data.sqlite')
# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# app.config['MAIL_SUBJECT_PREFIX'] = '[Tracker]'
# app.config['MAIL_SENDER'] = 'Tracker Admin <dannyx@gmail.com>'
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT']=587
# app.config['MAIL_USE_TLS']=True
# app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')
# app.config['UPLOAD_FOLDER']='uploads/'
#
#
#
# manager = Manager(app)
# bootstrap = Bootstrap(app)
# moment = Moment(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# manager.add_command('db', MigrateCommand)
# mail = Mail(app)
#
# status_dict = {0:'Status',
# 1:'Confirmed',
# 2:'Shipped',
# 3:'Delivered',
# 4:'Preparing Importation',
# 5:'Complete'}
#
# class PO_line(db.Model):
#     __tablename__='pos'
#     id = db.Column(db.Integer, primary_key=True)
#     po_number = db.Column(db.String(16), unique=True)
#     buyer = db.Column(db.String(2))
#     vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
#     pn = db.Column(db.String(16))
#     description = db.Column(db.String(64))
#     po_date = db.Column(db.DateTime(), default=datetime.utcnow)
#     qty_ordered = db.Column(db.Integer)
#     qty_received = db.Column(db.Integer)
#     balance = db.Column(db.Integer)
#     expected_del_date = db.Column(db.DateTime(), default=None, nullable=True)
#     ship_via_id = db.Column(db.Integer, db.ForeignKey('ship_vias.id'))
#     tracking_number = db.Column(db.String(32), default=None, nullable=True)
#     status = db.Column(db.Integer, default=0)
#     priority = db.Column(db.Boolean, default=False)
#     notes = db.Column(db.Text, default=None, nullable=True)
#     packing_slip_id = db.Column(db.Integer, db.ForeignKey('packing_slips.id'), nullable=True, default=None)
#     coo_id = db.Column(db.Integer, db.ForeignKey('coos.id'), nullable=True, default=None)
#
#     @staticmethod
#     def on_status_change(target, value, oldvalue, initiator):
#         print("PO# {}, Old Status: {}, New Status: {}.".format(target.po_number, oldvalue, value))
#         if value is None:
#             newstatus=status_dict[0]
#         else:
#             newstatus=status_dict[value]
#         if oldvalue is None:
#             oldstatus=status_dict[0]
#         else:
#             oldstatus=status_dict[value]
#         send_email('daniel.lopez@belf.com', 'PO# %s Status Update' % target.po_number, 'status_update', po_line=target, oldstatus=oldstatus, newstatus=newstatus)
#
#
#
# class Vendor(db.Model):
#     __tablename__ = 'vendors'
#     id = db.Column(db.Integer, primary_key=True)
#     vendor_number = db.Column(db.Integer, unique=True)
#     name = db.Column(db.String(64))
#     contact = db.Column(db.String(32), nullable=True, default=None)
#     email = db.Column(db.String(64), nullable=True, default=None)
#     website = db.Column(db.String(64), nullable=True, default=None)
#     phone = db.Column(db.String(16), nullable=True, default=None)
#     po_lines = db.relationship('PO_line', backref='vendor', lazy='dynamic')
#     default_ship_via_id = db.Column(db.Integer, db.ForeignKey('ship_vias.id'))
#
# class Ship_via(db.Model):
#     __tablename__ = 'ship_vias'
#     id = db.Column(db.Integer, primary_key=True)
#     code = db.Column(db.String(4), unique=True, nullable=False)
#     name = db.Column(db.String(32), nullable=False)
#     tracking_url = db.Column(db.String(64), default=None, nullable=True)
#     po_lines = db.relationship('PO_line', backref='ship_via', lazy='dynamic')
#     default_ship_via = db.relationship('Vendor', backref='default_ship_via', lazy='dynamic')
#
# class Packing_slip(db.Model):
#     __tablename__ ='packing_slips'
#     id = db.Column(db.Integer, primary_key=True)
#     delivery_date = db.Column(db.DateTime(),default=datetime.utcnow)
#     notes = db.Column(db.String(128), default=None, nullable=True)
#     po_lines = db.relationship('PO_line',backref='packing_slip', lazy='dynamic')
#
# class Coo(db.Model):
#     __tablename__ ='coos'
#     id = db.Column(db.Integer, primary_key=True)
#     vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
#     effective_since = db.Column(db.DateTime(),default=datetime.utcnow)
#     effective_until = db.Column(db.DateTime(), default=None, nullable=True)
#     valid = db.Column(db.Boolean)
#     po_lines = db.relationship('PO_line',backref='coo', lazy='dynamic')
#
# class Temp(db.Model):
#     __tablename__ = 'temp'
#     id = db.Column(db.Integer,primary_key=True)
#
# class PO_lineForm(Form):
#     qty_received = IntegerField('Qty Received', validators=[NumberRange(min=0)])
#     apply_to_all_order = BooleanField('Apply to all the order?',default=False)
#     expected_del_date = DateField('Expected Delivery Date', validators=[Optional()],format='%m/%d/%y', widget=DatePickerWidget())
#     ship_via = SelectField('Ship via', coerce=int, validators=[Optional()])
#     tracking_number = StringField('Tracking Number', validators=[Optional()])
#     status = SelectField('Status', coerce=int)
#     priority = BooleanField('High Priority')
#     notes = TextAreaField('Notes', validators=[Optional()])
#     submit = SubmitField('Submit')
#
#     def __init__(self, po_line, *args, **kwargs):
#         super(PO_lineForm, self).__init__(*args, **kwargs)
#         self.ship_via.choices = [(ship_via.id, ship_via.name) for ship_via in Ship_via.query.order_by(Ship_via.name).all()]
#         self.status.choices = [(0,"Ordered"),(1,"Confirmed"), (2,"Shipped"), (3,"Delivered"), (4,"Preparing Import"), (5,"Complete"),(6,"Cancelled")]
#         self.po_line=po_line
#
# class New_VendorForm(Form):
#     vendor_number = IntegerField('Vendor#', validators=[Required(),NumberRange(min=10000)])
#     name = StringField('Name', validators=[Required()])
#     contact = StringField('Contact name', validators=[Optional()])
#     email = StringField('Contact email', validators=[Optional(), Email()])
#     website = StringField('Website', validators=[Optional(), URL()])
#     phone =  StringField('Phone', validators=[Optional(),Length(10)])
#     default_ship_via_id = SelectField('Default Ship via', coerce=int)
#     submit = SubmitField('Submit')
#
#     def __init__(self, *args, **kwargs):
#         super(New_VendorForm, self).__init__(*args, **kwargs)
#         self.default_ship_via_id.choices = [(ship_via.id, ship_via.name) for ship_via in Ship_via.query.order_by(Ship_via.name).all()]
#
#     def validate_vendor_number(self, field):
#         if Vendor.query.filter_by(vendor_number=field.data).first():
#             raise ValidationError('Vendor# {} is already registered.'.format(field.data))
#
#     def validate_name(self, field):
#         if Vendor.query.filter_by(name=field.data).first():
#             raise ValidationError('Vendor {} is already registered.'.format(field.data))
#
# class FileUpload_Form(Form):
#     fileUpload = FileField('Select file: ')
#     submit = SubmitField('Submit')
#
# class NewShipVia_Form(Form):
#     code = StringField('Ship Via Code', validators=[Required()])
#     name = StringField('Ship Via Name', validators=[Required()])
#     tracking_url = StringField('Tracking URL', validators=[Optional()])
#     submit = SubmitField('Submit')
#
# def make_shell_context():
#     return dict(app=app, db=db, PO_line=PO_line, Vendor=Vendor, Ship_via=Ship_via, Packing_slip=Packing_slip, Coo=Coo)
# manager.add_command("shell", Shell(make_context=make_shell_context))
#
# @app.route('/', methods=['GET','POST'])
# def index():
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         old_name = session['name']
#         session['name'] = form.name.data
#         if old_name is not None and old_name != session['name']:
#             flash('Did you just changed your name??')
#         return redirect(url_for('index'))
#     return render_template('index.html', current_time =datetime.utcnow(), form=form, name=session.get('name'))
#
# @app.route('/orders/')
# def orders():
#     orders = PO_line.query.filter(PO_line.status < 5).order_by(PO_line.expected_del_date.asc()).all()
#     return render_template('orders.html', orders=orders)
#
# @app.route('/view_orders/', methods=['GET','POST'])
# def view_orders():
#     status=int(request.form['status'])
#     orders=[]
#     if status==9 or status is None:
#         orders = PO_line.query.filter(PO_line.status < 5).order_by(PO_line.expected_del_date.asc()).all()
#     else:
#         orders = PO_line.query.filter_by(status=status).all()
#     return render_template('_view_orders.html', orders=orders)
#
# @app.route('/view_shipvias/')
# def view_shipvias():
#     ship_vias = Ship_via.query.all()
#     return render_template('ship_vias.html', ship_vias=ship_vias)
#
# @app.route('/view_vendors/')
# def view_vendors():
#     vendors = Vendor.query.all()
#     return render_template('vendors.html', vendors=vendors)
#
#
#
#
# @app.route('/edit_ship_via/<int:id>', methods=['GET','POST'])
# def edit_ship_via(id):
#     ship_via = Ship_via.query.get_or_404(id)
#     form = NewShipVia_Form()
#     if form.validate_on_submit():
#         if form.code.data != ship_via.code:
#             s = Ship_via.query.filter_by(code=form.code.data).first()
#             if s is not None:
#                 flash("Ship via code '{}' is already registered.".format(form.code.data))
#         else:
#             ship_via.code =form.code.data
#             ship_via.name = form.name.data
#             ship_via.tracking_url = form.tracking_url.data
#             db.session.add(ship_via)
#             db.session.commit()
#             flash ("Ship via '{}' has been updated.".format(form.name.data))
#         ship_vias = Ship_via.query.all()
#         return render_template('ship_vias.html', ship_vias=ship_vias)
#     else:
#         form.code.data = ship_via.code
#         form.name.data = ship_via.name
#         form.tracking_url.data = ship_via.tracking_url
#         return render_template('edit_ship_via.html',form=form)
#
# @app.route('/new_shipvia/', methods=['GET','POST'])
# def new_shipvia():
#     form = NewShipVia_Form()
#     if form.validate_on_submit():
#         s = Ship_via.query.filter_by(code=form.code.data).first()
#         if s is None:
#             s = Ship_via(code=form.code.data, name=form.name.data, tracking_url=form.tracking_url.data)
#             db.session.add(s)
#             db.session.commit()
#             flash('{} has been registered.'.format(form.name.data))
#             return redirect(url_for('orders'))
#         else:
#             flash('Ship via: {} was already registered.'.format(form.code.data))
#             return redirect(url_for('orders'))
#     else:
#         return render_template('new_shipvia.html',form=form)
#
# @app.route('/new_vendor/', methods=['GET','POST'])
# def new_vendor():
#     form = New_VendorForm()
#     if form.validate_on_submit():
#         v = Vendor(vendor_number=form.vendor_number.data, name=form.name.data, contact=form.contact.data, email=form.email.data, website=form.website.data, phone=form.phone.data, default_ship_via_id=form.default_ship_via_id.data)
#         db.session.add(v)
#         db.session.commit()
#         flash("Vendor '{}' has been saved.".format(v.name))
#         return redirect(url_for('view_vendors'))
#     else:
#         return render_template('new_vendor.html',form=form)
#
#
# @app.route('/order/<int:id>', methods=['GET','POST'])
# def order(id):
#     po_line = PO_line.query.get_or_404(id)
#     form = PO_lineForm(po_line=po_line)
#     if form.validate_on_submit():
#         po_line.qty_received = form.qty_received.data
#         po_line.balance = po_line.qty_ordered-po_line.qty_received
#         po_line.expected_del_date = form.expected_del_date.data
#         print("Date: " , form.expected_del_date.data)
#         po_line.ship_via_id = form.ship_via.data
#         po_line.tracking_number = form.tracking_number.data
#         po_line.status = form.status.data
#         po_line.priority = form.priority.data
#         po_line.notes = form.notes.data
#         print(form.apply_to_all_order.data)
#         if form.apply_to_all_order.data:
#             print(po_line.po_number[:6])
#             items = PO_line.query.filter(PO_line.po_number.like(po_line.po_number[:6]+'%')).all()
#             for i in items:
#                 print(i.po_number)
#                 i.expected_del_date= form.expected_del_date.data
#                 i.status = form.status.data
#                 i.ship_via_id = form.ship_via.data
#                 i.tracking_number = form.tracking_number.data
#                 i.priority = form.priority.data
#                 i.notes = form.notes.data
#                 db.session.add(i)
#             db.session.commit()
#             flash('All the items on PO# {} have been updated.'.format(po_line.po_number[:6]))
#         else:
#             db.session.add(po_line)
#             db.session.commit()
#             flash('Order# %s has been updated.' % po_line.po_number)
#         return redirect(url_for('orders'))
#     form.qty_received.data = po_line.qty_received
#     form.expected_del_date.data = po_line.expected_del_date
#     form.ship_via.data = po_line.ship_via_id
#     form.tracking_number.data = po_line.tracking_number
#     form.status.data = po_line.status
#     form.priority.data = po_line.priority
#     form.notes.data = po_line.notes
#     return render_template('order.html',form=form, po_line=po_line)
#
# @app.route('/import/', methods=['GET','POST'])
# def import_file():
#     form =FileUpload_Form()
#     if form.validate_on_submit():
#         if 'fileUpload' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['fileUpload']
#         if file.filename == '':
#             flash('No selected file.')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             import_data(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('orders'))
#     return render_template('import.html', form=form)
#
#
#
#
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'),404
#
# @app.errorhandler(500)
# def internal_error(e):
#     return render_template('500.html'),500
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
#
# def import_data(filename):
#     import re
#     r = re.compile('.+A[0-9]{5}')
#     ship_via_na = Ship_via.query.filter_by(code='NA').first()
#     with open(filename)as f:
#         for line in f:
#             mo = r.match(line)
#             if mo is not None:
#                 pn = line[0:20].strip()
#                 if len(pn)>3 and pn[-3:]=='|41':
#                     pn=pn[:-3]
#                 po_number = line[20:34].strip()
#                 po_date=datetime.strptime(line[34:43].strip(),'%m-%d-%y')
#                 buyer = line[43:46].strip()
#                 vendor_number=int(line[46:53].strip())
#                 description = line[53:72].strip()
#                 expected_del_date = datetime.strptime(line[72:81].strip(),'%m-%d-%y')
#                 qty_ordered = get_qty(line[81:89].strip())
#                 qty_received = get_qty(line[89:97].strip())
#                 balance = get_qty(line[97:106].strip())
#                 if balance == 1 and vendor_number ==12612:
#                     continue    #skip blanket order helpers.
#                 p = PO_line.query.filter_by(po_number=po_number).first()
#                 if p is not None:
#                     p.expected_del_date = expected_del_date
#                     p.qty_ordered = qty_ordered
#                     p.qty_received = qty_received
#                     p.balance = balance
#                     db.session.add(p)
#                 else:
#                     v = Vendor.query.filter_by(vendor_number=vendor_number).first()
#                     if v is None:
#                         flash("Vendor# {} is not registered. Please insert this vendor before importing.".format(vendor_number))
#                         return
#                     p = PO_line(po_number=po_number, pn=pn, po_date=po_date, buyer=buyer, vendor_id=v.id, description=description, expected_del_date=expected_del_date, qty_ordered=qty_ordered, qty_received=qty_received, balance=balance, ship_via_id=v.default_ship_via_id,status=0,tracking_number='')
#                     db.session.add(p)
#     db.session.commit()
#     flash('File has been imported.')
#
#
# def get_qty(s):
#     if s == '':
#         return 0
#     else:
#         return int(s.strip().replace(',',''))
#
# def send_email(to, subject, template, **kwargs):
#     msg = Message(app.config['MAIL_SUBJECT_PREFIX']+subject, sender=app.config['MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template+'.txt', **kwargs)
#     msg.html = render_template(template+'.html', **kwargs)
#     thr = Thread(target=send_async_email,args=[app,msg])
#     thr.start()
#     return thr
#
# def send_async_email(app, msg):
#     with app.app_context():
#         mail.send(msg)
#
# db.event.listen(PO_line.status, 'set', PO_line.on_status_change)
#
# if __name__ == '__main__':
#     manager.run()
