from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from models import Country

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    company = StringField('Company/Organization', validators=[DataRequired(), Length(max=100)])
    country = SelectField('Country', validators=[DataRequired()], choices=[])
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    newsletter_consent = BooleanField('Subscribe to privacy updates and newsletters')
    terms_consent = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[DataRequired()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Populate country choices (alphabetically arranged)
        countries = [
            ('DZ', 'Algeria'),
            ('AO', 'Angola'),
            ('BW', 'Botswana'),
            ('BF', 'Burkina Faso'),
            ('BF', 'Burundi'),
            ('CM', 'Cameroon'),
            ('CV', 'Cape Verde'),
            ('CF', 'Central African Republic'),
            ('TD', 'Chad'),
            ('KM', 'Comoros'),
            ('CG', 'Republic of the Congo'),
            ('CD', 'Democratic Republic of the Congo'),
            ('CI', 'Côte d\'Ivoire'),
            ('DJ', 'Djibouti'),
            ('EG', 'Egypt'),
            ('GQ', 'Equatorial Guinea'),
            ('ER', 'Eritrea'),
            ('SZ', 'Eswatini'),
            ('ET', 'Ethiopia'),
            ('GA', 'Gabon'),
            ('GM', 'Gambia'),
            ('GH', 'Ghana'),
            ('GN', 'Guinea'),
            ('GW', 'Guinea-Bissau'),
            ('KE', 'Kenya'),
            ('LS', 'Lesotho'),
            ('LR', 'Liberia'),
            ('LY', 'Libya'),
            ('MG', 'Madagascar'),
            ('MW', 'Malawi'),
            ('ML', 'Mali'),
            ('MU', 'Mauritius'),
            ('MA', 'Morocco'),
            ('MZ', 'Mozambique'),
            ('NA', 'Namibia'),
            ('NE', 'Niger'),
            ('NG', 'Nigeria'),
            ('RW', 'Rwanda'),
            ('ST', 'São Tomé and Príncipe'),
            ('SC', 'Seychelles'),
            ('SL', 'Sierra Leone'),
            ('SO', 'Somalia'),
            ('ZA', 'South Africa'),
            ('SS', 'South Sudan'),
            ('SD', 'Sudan'),
            ('TZ', 'Tanzania'),
            ('TN', 'Tunisia'),
            ('UG', 'Uganda'),
            ('ZM', 'Zambia'),
            ('ZW', 'Zimbabwe'),
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