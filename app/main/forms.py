from flask_wtf import Form
from wtforms import StringField, IntegerField, SubmitField, BooleanField, TextAreaField, SelectField, FileField, DateField
from ..models import Ship_via, Vendor, User, Role
from wtforms.validators import Required, NumberRange, Optional, Email, URL, Length, Regexp
from wtforms import ValidationError

class PO_lineForm(Form):
    qty_received = IntegerField('Qty Received', validators=[NumberRange(min=0)])
    apply_to_all_order = BooleanField('Apply to all the order?',default=False)
    expected_del_date = DateField('Expected Delivery Date', validators=[Optional()],format='%m/%d/%y')
    ship_via = SelectField('Ship via', coerce=int, validators=[Optional()])
    tracking_number = StringField('Tracking Number', validators=[Optional()])
    status = SelectField('Status', coerce=int)
    priority = BooleanField('High Priority')
    submit = SubmitField('Submit')

    def __init__(self, po_line, *args, **kwargs):
        super(PO_lineForm, self).__init__(*args, **kwargs)
        self.ship_via.choices = [(ship_via.id, ship_via.name) for ship_via in Ship_via.query.order_by(Ship_via.name).all()]
        self.status.choices = [(0,"Ordered"),(1,"Confirmed"), (2,"Shipped"), (3,"Delivered"), (4,"Preparing Import"), (5,"Complete"),(6,"Cancelled")]
        self.po_line=po_line

class New_VendorForm(Form):
    vendor_number = IntegerField('Vendor#', validators=[Required(),NumberRange(min=10000)])
    name = StringField('Name', validators=[Required()])
    contact = StringField('Contact name', validators=[Optional()])
    email = StringField('Contact email', validators=[Optional(), Email()])
    website = StringField('Website', validators=[Optional(), URL()])
    phone =  StringField('Phone', validators=[Optional(),Length(10)])
    default_ship_via_id = SelectField('Default Ship via', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(New_VendorForm, self).__init__(*args, **kwargs)
        self.default_ship_via_id.choices = [(ship_via.id, ship_via.name) for ship_via in Ship_via.query.order_by(Ship_via.name).all()]

    def validate_vendor_number(self, field):
        if Vendor.query.filter_by(vendor_number=field.data).first():
            raise ValidationError('Vendor# {} is already registered.'.format(field.data))

    def validate_name(self, field):
        if Vendor.query.filter_by(name=field.data).first():
            raise ValidationError('Vendor {} is already registered.'.format(field.data))

class Edit_VendorForm(Form):
    vendor_number = IntegerField('Vendor#', validators=[Required(),NumberRange(min=10000)])
    name = StringField('Name', validators=[Required()])
    contact = StringField('Contact name', validators=[Optional()])
    email = StringField('Contact email', validators=[Optional(), Email()])
    website = StringField('Website', validators=[Optional(), URL()])
    phone =  StringField('Phone', validators=[Optional(),Length(10)])
    default_ship_via_id = SelectField('Default Ship via', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, vendor, *args, **kwargs):
        super(Edit_VendorForm, self).__init__(*args, **kwargs)
        self.default_ship_via_id.choices = [(ship_via.id, ship_via.name) for ship_via in Ship_via.query.order_by(Ship_via.name).all()]
        self.vendor = vendor

    def validate_vendor_number(self, field):
        if field.data != self.vendor.vendor_number and Vendor.query.filter_by(vendor_number=field.data).first():
            raise ValidationError('Vendor# {} is already registered.'.format(field.data))

    def validate_name(self, field):
        if field.data != self.vendor.name and Vendor.query.filter_by(name=field.data).first():
            raise ValidationError("Vendor '{}' is already registered.".format(field.data))

class FileUpload_Form(Form):
    fileUpload = FileField('Select file: ')
    submit = SubmitField('Submit')

class NewShipVia_Form(Form):
    code = StringField('Ship Via Code', validators=[Required()])
    name = StringField('Ship Via Name', validators=[Required()])
    tracking_url = StringField('Tracking URL', validators=[Optional()])
    submit = SubmitField('Submit')

class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0,64)])
    position = StringField('Position', validators=[Length(0,64)])
    submit = SubmitField('Submit')

class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email(), Regexp(r'^[A-Za-z0-9_.]*@belf\.com$',0,"Email address domain must be part of 'belf.com'")])
    username = StringField('Username', validators=[Required(), Length(1,64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters, numbers, dots or underscores.')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField('Real name', validators=[Length(0,64)])
    position = StringField('Position', validators=[Length(0,64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')
