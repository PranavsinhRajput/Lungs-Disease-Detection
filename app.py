from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
import datetime
import functools

app = Flask(__name__, 
            static_folder='static',  # Explicitly set static folder
            static_url_path='/static')

# Set a secret key for session management
app.secret_key = 'your_very_secure_secret_key_here'  # Change this to a random string in production

# Temporary folder to store uploaded images
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Hard-coded admin credentials
ADMIN_USERNAME = "kit"
ADMIN_PASSWORD = "aiml"

# Login required decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy function to replace save_prediction
def save_prediction(name, age, gender, prediction, disease_name, confidence, image_path):
    print("Database functionality under maintenance - prediction not saved")
    pass

# Dummy function to replace get_predictions
def get_predictions():
    print("Database functionality under maintenance - no predictions available")
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/user_details')
def user_details():
    return render_template('user_details.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Get user details from the form
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    
    # Pass these details to the upload image page
    return render_template('upload_image.html', name=name, age=age, gender=gender)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials against hardcoded values
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('history'))
        else:
            error = 'Invalid username or password. Please try again.'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    # Get prediction history from database (now returns empty list)
    history_data = get_predictions()
    
    # Add a message about database maintenance
    maintenance_message = "Database functionality under maintenance"
    
    return render_template('history.html', 
                         history_data=history_data, 
                         username=session.get('username'),
                         maintenance_message=maintenance_message)

@app.route('/process_image', methods=['POST'])
def process_image():
    # Collect user details from hidden fields
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')

    # Check if an image is uploaded
    if 'image' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Dummy prediction logic (replacing deep learning model)
        try:
            # Generate dummy prediction data
            disease_name = "DUMMY_DISEASE"
            confidence_str = "85.42%"
            prediction_result = "Positive (Dummy Data)"
            
            # Get relative image path
            relative_image_path = f'/static/uploads/{filename}'
            
            # Dummy save to database (will just print maintenance message)
            save_prediction(name, int(age), gender, prediction_result, disease_name, 
                           confidence_str, relative_image_path)
            
            return render_template('prediction.html', 
                                name=name, 
                                age=age, 
                                gender=gender, 
                                image_url=relative_image_path, 
                                prediction=prediction_result, 
                                disease_name=disease_name,
                                confidence=confidence_str,
                                dummy_message="This is dummy prediction data - Model functionality under maintenance")
        except Exception as e:
            return f"Error in prediction: {str(e)}", 500

    return "Invalid file format", 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)