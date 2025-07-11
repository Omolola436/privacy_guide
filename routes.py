import os
import json
import stripe
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import app, db, login_manager, mail
from models import User, Assessment, Service, Booking, AssessmentQuestion
from forms import LoginForm, RegistrationForm, AssessmentForm, BookingForm, NewsletterForm
from assessment import AssessmentEngine
from flask_mail import Message

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Landing page - Login/Register page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Redirect to login page as the main entry point
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists. Please choose different ones.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.company = form.company.data
        user.country = form.country.data
        user.phone = form.phone.data
        user.newsletter_consent = form.newsletter_consent.data
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by username or email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)
        
        flash('Invalid username/email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's latest assessment
    latest_assessment = Assessment.query.filter_by(user_id=current_user.id).order_by(
        Assessment.completed_at.desc()
    ).first()
    
    return render_template('dashboard.html', assessment=latest_assessment)

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    """Privacy posture assessment"""
    if request.method == 'POST':
        # Process assessment responses
        responses = {}
        
        # Get all form data that starts with 'question_'
        for key, value in request.form.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                responses[question_id] = value
        
        if not responses:
            flash('Please answer at least one question.', 'warning')
            return redirect(url_for('assessment'))
        
        # Calculate score and generate recommendations
        score, risk_level = AssessmentEngine.calculate_score(responses, current_user.country)
        recommendations = AssessmentEngine.generate_recommendations(score, risk_level, current_user.country)
        
        # Save assessment
        assessment_record = AssessmentEngine.create_assessment_record(
            current_user.id, responses, score, risk_level, recommendations
        )
        
        return redirect(url_for('results', assessment_id=assessment_record.id))
    
    # GET request - show assessment form
    questions = AssessmentEngine.get_questions()
    return render_template('assessment.html', questions=questions)

@app.route('/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    """Assessment results page"""
    assessment = Assessment.query.filter_by(
        id=assessment_id, 
        user_id=current_user.id
    ).first_or_404()
    
    recommendations = json.loads(assessment.recommendations) if assessment.recommendations else []
    
    return render_template('results.html', assessment=assessment, recommendations=recommendations)

@app.route('/services')
def services():
    """Premium services page"""
    # Create default services if none exist
    if Service.query.count() == 0:
        create_default_services()
    
    services = Service.query.filter_by(is_active=True).all()
    return render_template('services.html', services=services)

@app.route('/booking/<int:service_id>', methods=['GET', 'POST'])
@login_required
def booking(service_id):
    """Service booking page"""
    service = Service.query.get_or_404(service_id)
    form = BookingForm()
    
    if form.validate_on_submit():
        # Create booking record
        booking_record = Booking()
        booking_record.user_id = current_user.id
        booking_record.service_id = service.id
        booking_record.notes = form.notes.data
        booking_record.status = 'pending'
        
        db.session.add(booking_record)
        db.session.commit()
        
        # Redirect to payment
        return redirect(url_for('create_checkout_session', booking_id=booking_record.id))
    
    return render_template('booking.html', service=service, form=form)

@app.route('/create-checkout-session/<int:booking_id>', methods=['POST', 'GET'])
@login_required
def create_checkout_session(booking_id):
    """Create Stripe checkout session"""
    booking_record = Booking.query.filter_by(
        id=booking_id, 
        user_id=current_user.id
    ).first_or_404()
    
    if not stripe.api_key:
        flash('Payment system is not configured. Please contact support.', 'warning')
        return redirect(url_for('services'))
    
    try:
        # Get domain for URLs
        domain = request.host_url.rstrip('/')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': booking_record.service.currency.lower(),
                    'product_data': {
                        'name': booking_record.service.name,
                        'description': booking_record.service.description,
                    },
                    'unit_amount': int(booking_record.service.price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain + url_for('payment_success', booking_id=booking_record.id),
            cancel_url=domain + url_for('payment_cancel', booking_id=booking_record.id),
            metadata={
                'booking_id': booking_record.id
            }
        )
        
        # Save session ID
        booking_record.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        flash(f'Payment system error: {str(e)}', 'danger')
        return redirect(url_for('services'))

@app.route('/payment/success/<int:booking_id>')
@login_required
def payment_success(booking_id):
    """Payment success page"""
    booking_record = Booking.query.filter_by(
        id=booking_id, 
        user_id=current_user.id
    ).first_or_404()
    
    # Update booking status
    booking_record.payment_status = 'paid'
    booking_record.status = 'confirmed'
    db.session.commit()
    
    # Send confirmation email
    try:
        send_booking_confirmation_email(booking_record)
    except Exception as e:
        app.logger.error(f"Failed to send confirmation email: {e}")
    
    return render_template('success.html', booking=booking_record)

@app.route('/payment/cancel/<int:booking_id>')
@login_required
def payment_cancel(booking_id):
    """Payment cancel page"""
    booking_record = Booking.query.filter_by(
        id=booking_id, 
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('cancel.html', booking=booking_record)

@app.route('/newsletter/subscribe', methods=['POST'])
def newsletter_subscribe():
    """Newsletter subscription"""
    form = NewsletterForm()
    if form.validate_on_submit():
        # Here you would typically integrate with an email service like Mailchimp
        # For now, we'll just store the email and show a success message
        flash('Successfully subscribed to our newsletter!', 'success')
    else:
        flash('Please enter a valid email address.', 'danger')
    
    return redirect(url_for('index'))

def create_default_services():
    """Create default premium services"""
    services_data = [
        {
            'name': 'Risk Assessment',
            'description': 'Comprehensive privacy risk assessment delivered through Zoom session with detailed written report covering compliance gaps and actionable recommendations.',
            'service_type': 'assessment'
        },
        {
            'name': 'Vendor Assessment',
            'description': 'Professional evaluation of your vendors\' data protection practices using structured forms and comprehensive checklists to ensure third-party compliance.',
            'service_type': 'assessment'
        },
        {
            'name': 'Policy Templates',
            'description': 'Ready-to-use privacy policy templates in PDF and Word formats, fully editable and customized for your country and industry requirements.',
            'service_type': 'template'
        },
        {
            'name': 'Staff Training',
            'description': 'Interactive privacy training sessions available both live and on-demand, covering data protection best practices tailored for African regulatory environments.',
            'service_type': 'training'
        },
        {
            'name': 'DPO-as-a-Service Inquiry',
            'description': 'Initial consultation inquiry form to discuss Data Protection Officer services and ongoing compliance support for your organization.',
            'service_type': 'consultation'
        }
    ]
    
    for service_data in services_data:
        service = Service()
        service.name = service_data['name']
        service.description = service_data['description']
        service.service_type = service_data['service_type']
        service.is_active = True
        db.session.add(service)
    
    db.session.commit()

def send_booking_confirmation_email(booking):
    """Send booking confirmation email"""
    if not app.config.get('MAIL_USERNAME'):
        return  # Email not configured
    
    try:
        msg = Message(
            'Booking Confirmation - Privacy Platform',
            recipients=[booking.user.email]
        )
        
        msg.body = f"""
        Dear {booking.user.first_name},
        
        Thank you for booking our {booking.service.name} service.
        
        Booking Details:
        - Service: {booking.service.name}
        - Price: {booking.service.currency} {booking.service.price}
        - Status: {booking.status.title()}
        
        We will contact you shortly to schedule your session.
        
        Best regards,
        Privacy Platform Team
        """
        
        mail.send(msg)
        
    except Exception as e:
        app.logger.error(f"Failed to send email: {e}")

@app.route('/country-info')
@login_required
def country_info():
    """Country-specific privacy law information"""
    country_data = get_country_privacy_info(current_user.country)
    return render_template('country_info.html', country_data=country_data)

def get_country_privacy_info(country_code):
    """Get privacy law information for a specific country"""
    country_info = {
        'NG': {
            'name': 'Nigeria',
            'law': 'Nigeria Data Protection Act (NDPA), 2023',
            'regulator': 'Nigeria Data Protection Commission (NDPC)',
            'requirements': [
                'If you collect people\'s personal information (like names, emails, phone numbers), you must get their permission.',
                'You must tell people what you plan to do with their data.',
                'You need to keep their data safe and private.',
                'If your business handles a lot of data, you must submit a data protection audit.',
                'Businesses should have a data protection officer or advisor.'
            ]
        },
        'KE': {
            'name': 'Kenya',
            'law': 'Data Protection Act, 2019',
            'regulator': 'Office of the Data Protection Commissioner (ODPC)',
            'requirements': [
                'Businesses must register with the regulator if they collect or process personal data regularly.',
                'You must ask for clear consent before collecting personal data.',
                'You should tell people how and why you are collecting their data.',
                'People can ask to see their data or ask you to delete it.',
                'You must protect the data from loss or misuse.'
            ]
        },
        'GH': {
            'name': 'Ghana',
            'law': 'Data Protection Act, 2012',
            'regulator': 'Data Protection Commission',
            'requirements': [
                'Businesses must register with the Data Protection Commission.',
                'You must tell people why you need their data and get their consent.',
                'Keep personal data secure.',
                'People have the right to see, correct, or delete their data.'
            ]
        },
        'ZA': {
            'name': 'South Africa',
            'law': 'Protection of Personal Information Act (POPIA)',
            'regulator': 'Information Regulator',
            'requirements': [
                'You must have a reason (legal basis) to collect personal data.',
                'Consent is one way to collect data legally.',
                'Businesses must appoint someone (Information Officer) to manage data protection.',
                'People can ask to see or correct their data.',
                'You must tell the regulator and affected people if data is stolen or lost.'
            ]
        },
        'ZW': {
            'name': 'Zimbabwe',
            'law': 'Data Protection Act, 2021',
            'regulator': 'POTRAZ',
            'requirements': [
                'You must tell people what data you are collecting and why.',
                'You need to ask for their permission.',
                'You must keep their data safe.',
                'You should notify authorities if data is lost or stolen.'
            ]
        },
        'ZM': {
            'name': 'Zambia',
            'law': 'Data Protection Act, 2021',
            'regulator': 'ZICTA',
            'requirements': [
                'Get permission before collecting personal data.',
                'Businesses may need to register with the regulator.',
                'People can ask to see or change their data.',
                'Protect personal data from misuse.'
            ]
        },
        'BW': {
            'name': 'Botswana',
            'law': 'Data Protection Act, 2018',
            'regulator': 'Data Protection Commissioner',
            'requirements': [
                'Register with the Commissioner if you process personal data.',
                'Get consent from people before using their data.',
                'Keep data confidential and secure.',
                'People can request access to their data.'
            ]
        },
        'TZ': {
            'name': 'Tanzania',
            'law': 'Personal Data Protection Act, 2022',
            'regulator': 'The Personal Data Protection Commission (PDPC)',
            'requirements': [
                'Ask for permission before collecting personal data.',
                'Tell people what you will use their data for.',
                'Keep their data safe and use it only for the intended purpose.'
            ]
        },
        'UG': {
            'name': 'Uganda',
            'law': 'Data Protection and Privacy Act, 2019',
            'regulator': 'The Personal Data Protection Office (PDPO)',
            'requirements': [
                'Get clear consent before collecting data.',
                'Let people access and correct their data.',
                'Take steps to protect data from unauthorized access.'
            ]
        },
        'RW': {
            'name': 'Rwanda',
            'law': 'Data Protection Law, 2021',
            'regulator': 'National Cyber Security Authority (NCSA)',
            'requirements': [
                'Tell people why you are collecting their data.',
                'Get their consent.',
                'Keep data secure.',
                'Let people see and manage their data.'
            ]
        },
        'ET': {
            'name': 'Ethiopia',
            'law': 'Personal Data Protection Proclamation (Not yet enforced)',
            'regulator': 'To be announced',
            'requirements': [
                'When it starts, businesses will need to get consent to collect data.',
                'People will have rights to access and correct their data.'
            ]
        },
        'EG': {
            'name': 'Egypt',
            'law': 'Data Protection Law, 2020',
            'regulator': 'Egypt Data Protection Center',
            'requirements': [
                'Businesses need permission from people to use their data.',
                'You must register your business and follow security rules.',
                'People can ask you to delete or correct their data.'
            ]
        },
        'MA': {
            'name': 'Morocco',
            'law': 'Law No. 09-08',
            'regulator': 'CNDP',
            'requirements': [
                'You must register data activities.',
                'Get permission before using personal data.',
                'Secure the data and allow people to access or correct it.'
            ]
        },
        'TN': {
            'name': 'Tunisia',
            'law': 'Organic Law No. 2004-63',
            'regulator': 'Tunisian data protection authority (INPDP)',
            'requirements': [
                'Notify the authority before collecting data.',
                'Ask for consent from data subjects.',
                'Allow individuals to access or fix their information.'
            ]
        },
        'DZ': {
            'name': 'Algeria',
            'law': 'Law No. 18-07',
            'regulator': 'Not fully functional yet',
            'requirements': [
                'You must get consent to collect data.',
                'People can ask to access or change their data.',
                'Wait for full implementation of the law and regulator.'
            ]
        },
        'SN': {
            'name': 'Senegal',
            'law': 'Law No. 2008-12',
            'regulator': 'CDP',
            'requirements': [
                'Register your business if handling personal data.',
                'Get people\'s permission before collecting their data.',
                'People can see or correct their personal data.'
            ]
        },
        'CI': {
            'name': 'Côte d\'Ivoire',
            'law': 'Law No. 2013-450',
            'regulator': 'ARTCI',
            'requirements': [
                'Tell people what data you collect and why.',
                'Ask for their consent.',
                'Register with the authority if processing personal data.',
                'Respect rights to access and deletion.'
            ]
        },
        'CM': {
            'name': 'Cameroon',
            'law': 'No dedicated data protection law yet (privacy rules under ICT Law)',
            'regulator': 'ANTIC (Cybersecurity)',
            'requirements': [
                'Ask for consent when collecting personal data.',
                'Keep the data safe and do not share without permission.',
                'A data protection law is being planned.'
            ]
        },
        'AO': {
            'name': 'Angola',
            'law': 'Data Protection Law, 2011',
            'regulator': 'To be fully operational',
            'requirements': [
                'Get permission before collecting personal data.',
                'People have the right to access their data.',
                'You must keep the data secure and confidential.'
            ]
        }
    }
    
    return country_info.get(country_code, {
        'name': 'Unknown',
        'law': 'Information not available',
        'regulator': 'Information not available',
        'requirements': ['Country-specific information is being updated. Please contact our support team for guidance.']
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
