from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure secret key

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# In-memory data storage
import random
import string

users = {}
admins = {}
vehicles = [
]

# In-memory storage for inquiries
inquiries = []

# In-memory storage for sent emails
sent_emails = []

import json
import os

# File path for storing reinspection requests
REINSPECTION_FILE = 'instance/reinspection_requests.json'

# Load reinspection requests from file or initialize empty list
def load_reinspection_requests():
    if os.path.exists(REINSPECTION_FILE):
        with open(REINSPECTION_FILE, 'r') as f:
            try:
                data = json.load(f)
                # Clean data: remove entries with missing or invalid owner_username
                cleaned = [req for req in data if req.get('owner_username') and isinstance(req.get('owner_username'), str) and req.get('owner_username').strip() != '']
                return cleaned
            except json.JSONDecodeError:
                return []
    else:
        return []

reinspection_requests = load_reinspection_requests()

def generate_referral_code(length=8):
    """Generate a random alphanumeric referral code."""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        # Ensure code is unique among users
        if not any(user.get('referral_code') == code for user in users.values()):
            return code

# In-memory storage for scrap metal prices (initial values)
scrap_metal_prices = {
    'steel': 35,
    'stainless_steel': 42.5,
    'aluminium': 100,
    'copper': 550,
    'brass': 325,
    'battery': 105,
    'tyres_good': 50,
    'tyres_average': 30,
    'tyres_poor': 10
}

# User structure: {username: {name, username, phone_number, password_hash, email}}
# Admin structure: {username: {name, username, password_hash}}
# Vehicle structure: {vehicle_number, vehicle_type, fuel_type, car_subtype, model, year, condition, scrap_reason, owner_username}

def login_required(role='user'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session or 'role' not in session:
                flash("Please log in to access this page.")
                return redirect(url_for('home'))
            if role == 'admin' and session.get('role') != 'admin':
                flash("Admin access required.")
                return redirect(url_for('home'))
            if role == 'user' and session.get('role') != 'user':
                flash("User access required.")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_email(to_email, subject, body):
    # Mock email sending function for testing purposes
    print(f"Mock send email to: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

@app.route('/send_quoted_price', methods=['POST'])
@login_required(role='admin')
def send_quoted_price():
    username = request.form.get('username')
    amount = request.form.get('amount')
    if not username or not amount:
        flash("Username and amount are required to send the email.")
        return redirect(url_for('admin_dashboard'))

    user = users.get(username)
    if not user:
        flash("User not found.")
        return redirect(url_for('admin_dashboard'))

    to_email = user.get('email')
    if not to_email:
        flash("User email not found.")
        return redirect(url_for('admin_dashboard'))

    subject = "Exact Quoted Price for Your Vehicle Scrap"
    body = f"Dear {user.get('name')},\n\nThe exact quoted price for your vehicle scrap is: ₹{amount}.\n\nThank you for using our service.\n\nBest regards,\nTelangana Innodatatics Vehicle Scrapping Portal"

    if send_email(to_email, subject, body):
        # Log sent email
        from datetime import datetime
        print(f"Logging sent email to {to_email} with subject {subject}")  # Debug log
        sent_emails.append({
            'to_email': to_email,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        # Mark vehicle as having exact quotation sent
        for v in vehicles:
            if v['owner_username'] == username:
                v['exact_quotation_sent'] = True
        flash("Mail sent successfully.")
    else:
        flash("Failed to send email. Please try again later.")

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        company_code = request.form.get('company_code')
        if not all([name, username, password, company_code]):
            error = "All fields including company code are required."
        elif company_code != "innodatatics123":
            error = "Invalid company code."
        elif username in admins:
            error = "Admin username already exists."
        else:
            password_hash = generate_password_hash(password)
            admins[username] = {
                'name': name,
                'username': username,
                'password_hash': password_hash
            }
           
            return redirect(url_for('admin_login'))
    return render_template('admin_register.html', error=error)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = admins.get(username)
        if admin and check_password_hash(admin['password_hash'], password):
            session['username'] = username
            session['role'] = 'admin'
            flash("Admin logged in successfully.")
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid admin username or password."
    return render_template('admin_login.html', error=error)

@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    error = None
    action = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'register':
            name = request.form.get('name')
            username = request.form.get('username')
            phone_number = request.form.get('phone_number')
            email = request.form.get('email')
            password = request.form.get('password')
            referral_code_input = request.form.get('referral_code')
            if not all([name, username, phone_number, email, password]):
                error = "All registration fields except referral code are required."
            elif username in users:
                error = "Username already exists. Please choose a different username."
            else:
                # Validate referral code if provided
                referrer_username = None
                if referral_code_input:
                    for user_key, user_val in users.items():
                        if user_val.get('referral_code') == referral_code_input:
                            referrer_username = user_key
                            break
                    if not referrer_username:
                        error = "Invalid referral code."
                        return render_template('login_register.html', error=error, action=action)

                password_hash = generate_password_hash(password)
                # Generate unique referral code for new user
                new_referral_code = generate_referral_code()
                users[username] = {
                    'name': name,
                    'username': username,
                    'phone_number': phone_number,
                    'email': email,
                    'password_hash': password_hash,
                    'referral_code': new_referral_code,
                    'referrals': [],
                    'referral_rewards': 0
                }
                # If referred by someone, add this user to referrer's referrals list and increment reward
                if referrer_username:
                    users[referrer_username]['referrals'].append(username)
                    users[referrer_username]['referral_rewards'] += 10  # Example reward points

                flash("Registration successful. Please log in.")
                return redirect(url_for('login_register'))
        elif action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            user = users.get(username)
            if user and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['role'] = 'user'
                flash("Logged in successfully.")
                return redirect(url_for('home'))
            else:
                error = "Invalid username or password. Please try again."
    return render_template('login_register.html', error=error, action=action)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    action = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'register':
            name = request.form.get('name')
            username = request.form.get('username')
            phone_number = request.form.get('phone_number')
            password = request.form.get('password')
            if not all([name, username, phone_number, password]):
                error = "All registration fields are required."
            elif username in users:
                error = "Username already exists. Please choose a different username."
            else:
                password_hash = generate_password_hash(password)
                users[username] = {
                    'name': name,
                    'username': username,
                    'phone_number': phone_number,
                    'password_hash': password_hash
                }
                flash("Registration successful. Please log in.")
                return redirect(url_for('home'))
        elif action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            user = users.get(username)
            if user and check_password_hash(user['password_hash'], password):
                session['username'] = username
                session['role'] = 'user'
                flash("Logged in successfully.")
                return redirect(url_for('home'))
            else:
                error = "Invalid username or password. Please try again."
    return render_template('home.html', error=error, action=action)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'vehicle_scrapping_app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','jfif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
@login_required(role='user')
def register():
    error = None
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        vehicle_type = request.form.get('vehicle_type')
        fuel_type = request.form.get('fuel_type')
        car_subtype = request.form.get('car_subtype')
        model = request.form.get('model')
        year = request.form.get('year')
        condition = request.form.get('condition')
        scrap_reason = request.form.get('scrap_reason')
        vehicle_weight = request.form.get('vehicle_weight')
        battery_condition = request.form.get('battery_condition')
        tyres_condition = request.form.get('tyres_condition')

        rc_image = request.files.get('rc_image')
        vehicle_images = request.files.getlist('vehicle_images')

        if not all([vehicle_number, vehicle_type, fuel_type, model, year, condition, scrap_reason, vehicle_weight, battery_condition, tyres_condition, rc_image]) or len(vehicle_images) < 2:
            error = "All fields and required images must be provided. Please upload RC image and at least 2 vehicle images."
        elif vehicle_type == 'Car' and not car_subtype:
            error = "Please select a car subtype."
        elif not allowed_file(rc_image.filename):
            error = "Invalid RC image file type."
        elif any(not allowed_file(img.filename) for img in vehicle_images):
            error = "One or more vehicle images have invalid file types."
        else:
            owner_username = session['username']

            # Ensure upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            # Save RC image
            rc_filename = secure_filename(rc_image.filename)
            rc_path = os.path.join(app.config['UPLOAD_FOLDER'], rc_filename)
            rc_image.save(rc_path)

            # Save vehicle images
            vehicle_image_paths = []
            for img in vehicle_images:
                filename = secure_filename(img.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img.save(filepath)
                vehicle_image_paths.append(filepath)

            new_vehicle = {
                'vehicle_number': vehicle_number,
                'vehicle_type': vehicle_type,
                'fuel_type': fuel_type,
                'car_subtype': car_subtype if vehicle_type == 'Car' else None,
                'model': model,
                'year': year,
                'condition': condition,
                'scrap_reason': scrap_reason,
                'vehicle_weight': float(vehicle_weight),
                'battery_condition': battery_condition,
                'tyres_condition': tyres_condition,
                'owner_username': owner_username,
                'rc_image': rc_path,
                'vehicle_images': vehicle_image_paths
            }
            vehicles.append(new_vehicle)
            flash("Vehicle registered successfully.")
            return redirect(url_for('list_vehicles'))
    return render_template('register.html', error=error)

@app.route('/vehicles')
@login_required(role='user')
def list_vehicles():
    owner_username = session['username']
    user_vehicles = []
    for v in vehicles:
        if v['owner_username'] == owner_username:
            # Check for any pending reinspection request for this vehicle and merge edited data
            vehicle_copy = v.copy()
            for req in reinspection_requests:
                if req.get('vehicle_number') == v['vehicle_number'] and req.get('owner_username') == owner_username and req.get('status') == 'Pending':
                    edited_data = req.get('edited_data', {})
                    for key, value in edited_data.items():
                        vehicle_copy[key] = value
                    if req.get('rc_image'):
                        vehicle_copy['rc_image'] = req['rc_image']
                    if req.get('vehicle_images'):
                        vehicle_copy['vehicle_images'] = req['vehicle_images']
                    break
            user_vehicles.append(vehicle_copy)
    user = users.get(owner_username)
    return render_template('vehicles.html', vehicles=user_vehicles, user=user)

@app.route('/vehicle/<vehicle_number>')
@login_required(role='user')
def vehicle_detail(vehicle_number):
    owner_username = session['username']
    vehicle = None
    for v in vehicles:
        if v['vehicle_number'] == vehicle_number and v['owner_username'] == owner_username:
            vehicle = v
            break
    if not vehicle:
        flash("Vehicle not found or access denied.")
        return redirect(url_for('list_vehicles'))

    # Check for any pending reinspection request for this vehicle and merge edited data
    for req in reinspection_requests:
        if req.get('vehicle_number') == vehicle_number and req.get('owner_username') == owner_username and req.get('status') == 'Pending':
            edited_data = req.get('edited_data', {})
            # Create a copy of vehicle to avoid modifying original
            vehicle = vehicle.copy()
            # Merge edited data into vehicle
            for key, value in edited_data.items():
                vehicle[key] = value
            # Update images if present in reinspection request
            if req.get('rc_image'):
                vehicle['rc_image'] = req['rc_image']
            if req.get('vehicle_images'):
                vehicle['vehicle_images'] = req['vehicle_images']
            break

    return render_template('vehicle_detail.html', vehicle=vehicle)

@app.route('/vehicle/<vehicle_number>/edit', methods=['GET', 'POST'])
@login_required(role='user')
def edit_vehicle(vehicle_number):
    owner_username = session['username']
    vehicle = None
    for v in vehicles:
        if v['vehicle_number'] == vehicle_number and v['owner_username'] == owner_username:
            vehicle = v
            break
    if not vehicle:
        flash("Vehicle not found or access denied.")
        return redirect(url_for('list_vehicles'))

    error = None
    if request.method == 'POST':
        # Find original vehicle data
        original_vehicle = None
        for v in vehicles:
            if v['vehicle_number'] == vehicle_number and v['owner_username'] == owner_username:
                original_vehicle = v
                break

        # Check if exact quotation email has been sent for this vehicle
        if original_vehicle and original_vehicle.get('exact_quotation_sent'):
            # Check if there is already a pending reinspection request for this vehicle
            for req in reinspection_requests:
                if req.get('vehicle_number') == vehicle_number and req.get('status') == 'Pending':
                    flash("There is already a pending reinspection request for this vehicle. Please wait for it to be processed before submitting a new one.")
                    return redirect(url_for('edit_vehicle', vehicle_number=vehicle_number))

            # Treat edit as reinspection request
            reinspection_data = {
                'vehicle_number': vehicle_number,
                'owner_username': owner_username,
                'original_data': original_vehicle if original_vehicle else {},
                'edited_data': {
                    'vehicle_type': request.form.get('vehicle_type'),
                    'fuel_type': request.form.get('fuel_type'),
                    'car_subtype': request.form.get('car_subtype'),
                    'model': request.form.get('model'),
                    'year': request.form.get('year'),
                    'condition': request.form.get('condition'),
                    'scrap_reason': request.form.get('scrap_reason'),
                    'vehicle_weight': float(request.form.get('vehicle_weight')),
                    'battery_condition': request.form.get('battery_condition'),
                    'tyres_condition': request.form.get('tyres_condition'),
                },
                'original_rc_image': original_vehicle.get('rc_image') if original_vehicle else None,
                'rc_image': None,
                'original_vehicle_images': original_vehicle.get('vehicle_images') if original_vehicle else [],
                'vehicle_images': [],
                'status': 'Pending'
            }

            # Handle RC image upload
            rc_image = request.files.get('rc_image')
            if rc_image and rc_image.filename != '':
                if allowed_file(rc_image.filename):
                    rc_filename = secure_filename(rc_image.filename)
                    rc_path = os.path.join(app.config['UPLOAD_FOLDER'], rc_filename)
                    rc_image.save(rc_path)
                    reinspection_data['rc_image'] = 'uploads/' + rc_filename
                else:
                    flash("Invalid RC image file type.")
                    return redirect(url_for('edit_vehicle', vehicle_number=vehicle_number))

            # Determine if RC image is added, removed, or unchanged
            if reinspection_data['original_rc_image'] and reinspection_data['rc_image']:
                if reinspection_data['original_rc_image'] != reinspection_data['rc_image']:
                    reinspection_data['rc_image_status'] = 'added'
                else:
                    reinspection_data['rc_image_status'] = 'unchanged'
            elif reinspection_data['original_rc_image'] and not reinspection_data['rc_image']:
                reinspection_data['rc_image_status'] = 'removed'
            elif not reinspection_data['original_rc_image'] and reinspection_data['rc_image']:
                reinspection_data['rc_image_status'] = 'added'
            else:
                reinspection_data['rc_image_status'] = 'unchanged'

            # Handle vehicle images upload
            vehicle_images = request.files.getlist('vehicle_images')
            if vehicle_images and any(img.filename != '' for img in vehicle_images):
                valid_images = []
                for img in vehicle_images:
                    if img and img.filename != '' and allowed_file(img.filename):
                        filename = secure_filename(img.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        img.save(filepath)
                        valid_images.append('uploads/' + filename)
                    else:
                        flash("One or more vehicle images have invalid file types.")
                        return redirect(url_for('edit_vehicle', vehicle_number=vehicle_number))
                if valid_images:
                    reinspection_data['vehicle_images'].extend(valid_images)

            # Determine added and removed vehicle images
            original_images = set(reinspection_data.get('original_vehicle_images', []))
            new_images = set(reinspection_data.get('vehicle_images', []))
            reinspection_data['added_images'] = list(new_images - original_images)
            reinspection_data['removed_images'] = list(original_images - new_images)
            reinspection_data['unchanged_images'] = list(original_images & new_images)

            print("Reinspection data to append:", reinspection_data)
            reinspection_requests.append(reinspection_data)
            flash("Reinspection request submitted successfully.")
            return redirect(url_for('vehicle_detail', vehicle_number=vehicle_number))
        else:
            # Normal edit flow - update vehicle data directly
            vehicle['vehicle_type'] = request.form.get('vehicle_type')
            vehicle['fuel_type'] = request.form.get('fuel_type')
            vehicle['car_subtype'] = request.form.get('car_subtype')
            vehicle['model'] = request.form.get('model')
            vehicle['year'] = request.form.get('year')
            vehicle['condition'] = request.form.get('condition')
            vehicle['scrap_reason'] = request.form.get('scrap_reason')
            vehicle['vehicle_weight'] = float(request.form.get('vehicle_weight'))
            vehicle['battery_condition'] = request.form.get('battery_condition')
            vehicle['tyres_condition'] = request.form.get('tyres_condition')

            # Handle RC image upload
            rc_image = request.files.get('rc_image')
            if rc_image and rc_image.filename != '':
                if allowed_file(rc_image.filename):
                    rc_filename = secure_filename(rc_image.filename)
                    rc_path = os.path.join(app.config['UPLOAD_FOLDER'], rc_filename)
                    rc_image.save(rc_path)
                    vehicle['rc_image'] = rc_path
                else:
                    flash("Invalid RC image file type.")
                    return redirect(url_for('edit_vehicle', vehicle_number=vehicle_number))

            # Handle vehicle images upload
            vehicle_images = request.files.getlist('vehicle_images')

            # Handle removal of selected images
            remove_images = request.form.getlist('remove_vehicle_images')
            print(f"Images marked for removal: {remove_images}")
            flash(f"{len(remove_images)} images marked for removal.")
            if remove_images:
                vehicle['vehicle_images'] = [img for img in vehicle['vehicle_images'] if img not in remove_images]

            if vehicle_images and any(img.filename != '' for img in vehicle_images):
                valid_images = []
                for img in vehicle_images:
                    if img and img.filename != '' and allowed_file(img.filename):
                        filename = secure_filename(img.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        img.save(filepath)
                        valid_images.append(filepath)
                    else:
                        flash("One or more vehicle images have invalid file types.")
                        return redirect(url_for('edit_vehicle', vehicle_number=vehicle_number))
                if valid_images:
                    vehicle['vehicle_images'].extend(valid_images)

            flash("Vehicle details updated successfully.")
            return redirect(url_for('vehicle_detail', vehicle_number=vehicle_number))

    return render_template('vehicle_edit.html', vehicle=vehicle, users=users)

@app.route('/quotation', methods=['GET', 'POST'])
@login_required(role='user')
def quotation():
    owner_username = session['username']
    user_vehicles = [v for v in vehicles if v['owner_username'] == owner_username]
    if not user_vehicles:
        flash("Please register a vehicle first to get a quotation.")
        return redirect(url_for('register'))

    selected_vehicle_number = None
    if request.method == 'POST':
        selected_vehicle_number = request.form.get('vehicle_number')
    elif request.method == 'GET':
        selected_vehicle_number = request.args.get('vehicle_number')

    vehicle = None
    if selected_vehicle_number:
        for v in user_vehicles:
            if v['vehicle_number'] == selected_vehicle_number:
                vehicle = v
                break
    if not vehicle:
        vehicle = user_vehicles[-1]  # fallback to most recent vehicle

    base_prices = {
        'Car': 5000,
        'Motorcycle': 2000,
        'Truck': 8000,
        'Bus': 10000,
        'Other': 3000
    }
    condition_multipliers = {
        'Excellent': 1.0,
        'Good': 0.8,
        'Fair': 0.5,
        'Poor': 0.3
    }
    # Scrap rates per kg (₹) - using provided Telangana rates
    scrap_rates = {
        'steel': 35,
        'stainless_steel': 42.5,  # average of 40 and 45
        'aluminium': 100,
        'copper': 550,  # average of 500 and 600
        'brass': 325,   # average of 300 and 350
        'battery': 105, # average of 80 and 130
        'tyres_good': 50,
        'tyres_average': 30,
        'tyres_poor': 10
    }
    # Base price from vehicle type
    base_price = base_prices.get(vehicle['vehicle_type'], 3000)
    # Condition multiplier
    multiplier = condition_multipliers.get(vehicle['condition'], 0.5)
    # Weight in kg
    weight = vehicle.get('vehicle_weight', 1000)  # default 1000kg if missing
    # Battery condition factor
    battery_condition = vehicle.get('battery_condition', 'Average')
    battery_factor = {
        'Good': 1.0,
        'Average': 0.7,
        'Poor': 0.4
    }.get(battery_condition, 0.7)
    # Tyres condition factor
    tyres_condition = vehicle.get('tyres_condition', 'Average')
    tyres_factor = {
        'Good': 1.0,
        'Average': 0.7,
        'Poor': 0.4
    }.get(tyres_condition, 0.7)
    # Calculate scrap value based on weight and steel rate
    scrap_value = weight * scrap_rates['steel']
    # Adjust scrap value by battery and tyres condition
    adjusted_value = scrap_value * battery_factor * tyres_factor
    # Adjust by base price and condition multiplier
    quotation_result = adjusted_value * multiplier * (base_price / 5000)  # normalize base price
    # Calculate price range ±10%
    lower_bound = quotation_result * 0.9
    upper_bound = quotation_result * 1.1
    price_range = f"₹{lower_bound:.2f} - ₹{upper_bound:.2f}"
    return render_template('quotation.html', quotation=price_range, vehicle=vehicle, user_vehicles=user_vehicles)

@app.route('/admin_dashboard')
@login_required(role='admin')
def admin_dashboard():
    # Prepare data for charts
    vehicle_types = {}
    total_prices = {}
    counts = {}
    condition_counts = {}
    battery_condition_counts = {}
    tyres_condition_counts = {}
    scrap_reason_counts = {}

    base_prices = {
        'Car': 5000,
        'Motorcycle': 2000,
        'Truck': 8000,
        'Bus': 10000,
        'Other': 3000
    }
    condition_multipliers = {
        'Excellent': 1.0,
        'Good': 0.8,
        'Fair': 0.5,
        'Poor': 0.3
    }
    scrap_rates = {
        'steel': 35,
        'stainless_steel': 42.5,
        'aluminium': 100,
        'copper': 550,
        'brass': 325,
        'battery': 105,
        'tyres_good': 50,
        'tyres_average': 30,
        'tyres_poor': 10
    }
    for v in vehicles:
        vehicle_type = v.get('vehicle_type')
        condition = v.get('condition')
        battery_condition = v.get('battery_condition', 'Average')
        tyres_condition = v.get('tyres_condition', 'Average')
        scrap_reason = v.get('scrap_reason', 'Unknown')

        if vehicle_type is None:
            continue  # skip invalid entries

        vehicle_types[vehicle_type] = vehicle_types.get(vehicle_type, 0) + 1
        base_price = base_prices.get(vehicle_type, 3000)
        multiplier = condition_multipliers.get(condition, 0.5)
        weight = v.get('vehicle_weight', 1000)
        battery_factor = {
            'Good': 1.0,
            'Average': 0.7,
            'Poor': 0.4
        }.get(battery_condition, 0.7)
        tyres_factor = {
            'Good': 1.0,
            'Average': 0.7,
            'Poor': 0.4
        }.get(tyres_condition, 0.7)
        scrap_value = weight * scrap_rates['steel']
        adjusted_value = scrap_value * battery_factor * tyres_factor
        price = adjusted_value * multiplier * (base_price / 5000)
        total_prices[vehicle_type] = total_prices.get(vehicle_type, 0) + price
        counts[vehicle_type] = counts.get(vehicle_type, 0) + 1

        # Count conditions for new charts
        if condition is not None:
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
        if battery_condition is not None:
            battery_condition_counts[battery_condition] = battery_condition_counts.get(battery_condition, 0) + 1
        if tyres_condition is not None:
            tyres_condition_counts[tyres_condition] = tyres_condition_counts.get(tyres_condition, 0) + 1
        if scrap_reason is not None:
            scrap_reason_counts[scrap_reason] = scrap_reason_counts.get(scrap_reason, 0) + 1

    average_prices = {}
    for vt in total_prices:
        average_prices[vt] = total_prices[vt] / counts[vt]

    # Prepare scrapPrices data for scrap metal prices chart
    scrapPrices = {
        'Steel': scrap_rates['steel'],
        'Stainless Steel': scrap_rates['stainless_steel'],
        'Aluminium': scrap_rates['aluminium'],
        'Copper': scrap_rates['copper'],
        'Brass': scrap_rates['brass'],
        'Battery': scrap_rates['battery'],
        'Tyres (Good)': scrap_rates['tyres_good'],
        'Tyres (Average)': scrap_rates['tyres_average'],
        'Tyres (Poor)': scrap_rates['tyres_poor']
    }

    pending_reinspection_count = sum(1 for req in reinspection_requests if req.get('owner_username') in users and req.get('status') == 'Pending')

    # Prepare referral data for admin dashboard
    referral_data = []
    for username, user in users.items():
        referral_data.append({
            'username': username,
            'name': user.get('name'),
            'referral_code': user.get('referral_code'),
            'referrals_count': len(user.get('referrals', [])),
            'referral_rewards': user.get('referral_rewards', 0)
        })

    # Ensure all reinspection_requests have required keys for template
    for req in reinspection_requests:
        if 'original_data' not in req:
            req['original_data'] = {}
        if 'original_rc_image' not in req:
            req['original_rc_image'] = None
        if 'rc_image' not in req:
            req['rc_image'] = None
        if 'original_vehicle_images' not in req:
            req['original_vehicle_images'] = []
        if 'vehicle_images' not in req:
            req['vehicle_images'] = []
        if 'rc_image_status' not in req:
            req['rc_image_status'] = 'unchanged'
        if 'added_images' not in req:
            req['added_images'] = []
        if 'removed_images' not in req:
            req['removed_images'] = []
        if 'unchanged_images' not in req:
            req['unchanged_images'] = []

    # Filter reinspection_requests to include only those with valid users and status 'Pending'
    valid_reinspection_requests = [req for req in reinspection_requests if req.get('owner_username') in users and req.get('status') == 'Pending']

    return render_template('admin_dashboard.html',
                           vehicle_types=vehicle_types,
                           vehicles=vehicles,
                           users=users,
                           average_prices=average_prices,
                           scrapPrices=scrapPrices,
                           inquiries=inquiries,
                           condition_counts=condition_counts,
                           battery_condition_counts=battery_condition_counts,
                           tyres_condition_counts=tyres_condition_counts,
                           scrap_reason_counts=scrap_reason_counts,
                           reinspection_requests=valid_reinspection_requests,
                           pending_reinspection_count=pending_reinspection_count,
                           referral_data=referral_data)

@app.route('/admin_logout')
@login_required(role='admin')
def admin_logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("Admin logged out successfully.")
    return redirect(url_for('admin_login'))

@app.route('/api/send_reinspection_email', methods=['POST'])
@login_required(role='admin')
def send_reinspection_email():
    data = request.get_json()
    username = data.get('username')
    vehicle_number = data.get('vehicle_number')
    status = data.get('status')
    email_content = data.get('email_content')

    if not username or not vehicle_number or not status or not email_content:
        return jsonify({'error': 'Missing required data'}), 400

    user = users.get(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    to_email = user.get('email')
    if not to_email:
        return jsonify({'error': 'User email not found'}), 404

    subject = f"Reinspection Request {status} Notification"

    # Send email (mocked)
    if send_email(to_email, subject, email_content):
        from datetime import datetime
        # Log sent email
        sent_emails.append({
            'to_email': to_email,
            'subject': subject,
            'body': email_content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        # Update reinspection request status to Completed
        for req in reinspection_requests:
            if req['vehicle_number'] == vehicle_number and req['owner_username'] == username:
                req['status'] = 'Completed'

                # Update main vehicle data with edited data from reinspection request
                for v in vehicles:
                    if v['vehicle_number'] == vehicle_number and v['owner_username'] == username:
                        edited_data = req.get('edited_data', {})
                        v['vehicle_type'] = edited_data.get('vehicle_type', v['vehicle_type'])
                        v['fuel_type'] = edited_data.get('fuel_type', v['fuel_type'])
                        v['car_subtype'] = edited_data.get('car_subtype', v.get('car_subtype'))
                        v['model'] = edited_data.get('model', v['model'])
                        v['year'] = edited_data.get('year', v['year'])
                        v['condition'] = edited_data.get('condition', v['condition'])
                        v['scrap_reason'] = edited_data.get('scrap_reason', v['scrap_reason'])
                        v['vehicle_weight'] = edited_data.get('vehicle_weight', v['vehicle_weight'])
                        v['battery_condition'] = edited_data.get('battery_condition', v['battery_condition'])
                        v['tyres_condition'] = edited_data.get('tyres_condition', v['tyres_condition'])

                        # Update RC image if changed
                        if req.get('rc_image'):
                            v['rc_image'] = req['rc_image']

                        # Update vehicle images if changed
                        if req.get('vehicle_images'):
                            v['vehicle_images'] = req['vehicle_images']
                        break

                # Save updated reinspection_requests to file
                with open(REINSPECTION_FILE, 'w') as f:
                    json.dump(reinspection_requests, f, indent=4)
                break

        return jsonify({'message': 'Email sent and status updated successfully.'}), 200
    else:
        return jsonify({'error': 'Failed to send email.'}), 500

@app.route('/admin_sent_emails')
@login_required(role='admin')
def admin_sent_emails():
    return render_template('admin_sent_emails.html', sent_emails=sent_emails)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        # Save inquiry to in-memory list
        inquiries.append({
            'name': name,
            'email': email,
            'phone': phone,
            'message': message
        })
        flash("Thank you for your inquiry. We will get back to you soon.")
        return render_template('contact_us.html')
    return render_template('contact_us.html')

@login_required(role='admin')
def admin_dashboard_view():
    # Prepare data for charts
    vehicle_types = {}
    total_prices = {}
    counts = {}
    base_prices = {
        'Car': 5000,
        'Motorcycle': 2000,
        'Truck': 8000,
        'Bus': 10000,
        'Other': 3000
    }
    condition_multipliers = {
        'Excellent': 1.0,
        'Good': 0.8,
        'Fair': 0.5,
        'Poor': 0.3
    }
    for v in vehicles:
        vehicle_types[v['vehicle_type']] = vehicle_types.get(v['vehicle_type'], 0) + 1
        base_price = base_prices.get(v['vehicle_type'], 3000)
        multiplier = condition_multipliers.get(v['condition'], 0.5)
        price = base_price * multiplier
        total_prices[v['vehicle_type']] = total_prices.get(v['vehicle_type'], 0) + price
        counts[v['vehicle_type']] = counts.get(v['vehicle_type'], 0) + 1
    average_prices = {}
    for vt in total_prices:
        average_prices[vt] = total_prices[vt] / counts[vt]
    return render_template('admin_dashboard.html', vehicle_types=vehicle_types, vehicles=vehicles, users=users, average_prices=average_prices, inquiries=inquiries)

if __name__ == '__main__':
    app.run(debug=True)
# Ensure all reinspection_requests have required keys for template
for req in reinspection_requests:
    if 'original_data' not in req:
        req['original_data'] = {}
    if 'original_rc_image' not in req:
        req['original_rc_image'] = None
    if 'rc_image' not in req:
        req['rc_image'] = None
    if 'original_vehicle_images' not in req:
        req['original_vehicle_images'] = []
    if 'vehicle_images' not in req:
        req['vehicle_images'] = []
    if 'rc_image_status' not in req:
        req['rc_image_status'] = 'unchanged'
    if 'added_images' not in req:
        req['added_images'] = []
    if 'removed_images' not in req:
        req['removed_images'] = []
    if 'unchanged_images' not in req:
        req['unchanged_images'] = []
