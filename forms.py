from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from models import Country

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    company = StringField('Company/Organization', validators=[Optional(), Length(max=100)])
    country = SelectField('Country', validators=[DataRequired()], choices=[])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    newsletter_consent = BooleanField('Subscribe to privacy updates and newsletters')
    terms_consent = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[DataRequired()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Populate country choices
        countries = [
            ('NG', 'Nigeria'),
            ('KE', 'Kenya'),
            ('GH', 'Ghana'),
            ('ZA', 'South Africa'),
            ('ZW', 'Zimbabwe'),
            ('ZM', 'Zambia'),
            ('BW', 'Botswana'),
            ('TZ', 'Tanzania'),
            ('UG', 'Uganda'),
            ('RW', 'Rwanda'),
            ('ET', 'Ethiopia'),
            ('EG', 'Egypt'),
            ('MA', 'Morocco'),
            ('TN', 'Tunisia'),
            ('DZ', 'Algeria'),
            ('SN', 'Senegal'),
            ('CI', 'Côte d\'Ivoire'),
            ('CM', 'Cameroon'),
            ('AO', 'Angola'),
            ('MZ', 'Mozambique'),
            ('MW', 'Malawi'),
            ('ZW', 'Zimbabwe'),
            ('NA', 'Namibia'),
            ('LS', 'Lesotho'),
            ('SZ', 'Eswatini'),
            ('MU', 'Mauritius'),
            ('SC', 'Seychelles'),
            ('MG', 'Madagascar'),
            ('LR', 'Liberia'),
            ('SL', 'Sierra Leone'),
            ('GN', 'Guinea'),
            ('BF', 'Burkina Faso'),
            ('ML', 'Mali'),
            ('NE', 'Niger'),
            ('TD', 'Chad'),
            ('CF', 'Central African Republic'),
            ('CG', 'Republic of the Congo'),
            ('CD', 'Democratic Republic of the Congo'),
            ('GA', 'Gabon'),
            ('GQ', 'Equatorial Guinea'),
            ('ST', 'São Tomé and Príncipe'),
            ('CV', 'Cape Verde'),
            ('GM', 'Gambia'),
            ('GW', 'Guinea-Bissau'),
            ('DJ', 'Djibouti'),
            ('SO', 'Somalia'),
            ('ER', 'Eritrea'),
            ('SS', 'South Sudan'),
            ('SD', 'Sudan'),
            ('LY', 'Libya'),
            ('KM', 'Comoros'),
            ('OTHER', 'Other')
        ]
        self.country.choices = [('', 'Select your country')] + countries

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class AssessmentForm(FlaskForm):
    submit = SubmitField('Submit Assessment')

class BookingForm(FlaskForm):
    service_id = SelectField('Service', validators=[DataRequired()], coerce=int)
    preferred_date = StringField('Preferred Date', validators=[DataRequired()])
    preferred_time = StringField('Preferred Time', validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Book Service')

class NewsletterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')