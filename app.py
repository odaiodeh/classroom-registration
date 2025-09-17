from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import io
import base64
import os
from database import Database
from utils import reshape_arabic_text, generate_qr_code, get_registration_url, CLASSES, COLORS, GRADE_COLORS
import json

app = Flask(__name__)
app.secret_key = 'school_secret_key_2024'  # Change this in production

# Initialize database
db = Database()

@app.route('/')
def home():
    """Home page with classroom cards"""
    all_students = db.get_all_classes_with_students()
    
    # Organize classes by grade
    grades = {
        'الرابع': [],
        'الخامس': [],
        'السادس': []
    }
    
    for class_name in CLASSES:
        students = all_students.get(class_name, [])
        class_info = {
            'name': class_name,
            'students': students,
            'count': len(students),
            'color': GRADE_COLORS.get(class_name.split()[0], '#3498db')
        }
        
        if 'الرابع' in class_name:
            grades['الرابع'].append(class_info)
        elif 'الخامس' in class_name:
            grades['الخامس'].append(class_info)
        elif 'السادس' in class_name:
            grades['السادس'].append(class_info)
    
    return render_template('home.html', grades=grades)

@app.route('/add_student', methods=['POST'])
def add_student():
    """Add a student to a class"""
    data = request.get_json()
    student_name = data.get('name', '').strip()
    class_name = data.get('class', '').strip()
    
    if not student_name or not class_name:
        return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات'})
    
    if class_name not in CLASSES:
        return jsonify({'success': False, 'message': 'الصف غير صحيح'})
    
    success = db.add_student(class_name, student_name)
    
    if success:
        # Log the registration for monitoring
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] New registration: {student_name} in {class_name}")
        
        return jsonify({'success': True, 'message': 'تمت إضافة الطالب بنجاح'})
    else:
        return jsonify({'success': False, 'message': 'الطالب موجود بالفعل'})

@app.route('/remove_student', methods=['POST'])
def remove_student():
    """Remove a student from a class"""
    data = request.get_json()
    student_name = data.get('name', '').strip()
    class_name = data.get('class', '').strip()
    password = data.get('password', '').strip()
    
    if not all([student_name, class_name, password]):
        return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات'})
    
    success, message = db.remove_student(class_name, student_name, password)
    
    return jsonify({'success': success, 'message': message})

@app.route('/get_students/<class_name>')
def get_students(class_name):
    """Get students for a specific class"""
    if class_name not in CLASSES:
        return jsonify({'success': False, 'message': 'الصف غير صحيح'})
    
    students = db.get_students(class_name)
    return jsonify({'success': True, 'students': students})

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for QR code access"""
    if request.method == 'GET':
        return render_template('register.html', classes=CLASSES)
    
    # POST request - handle registration
    data = request.get_json() if request.is_json else request.form
    student_name = data.get('name', '').strip()
    class_name = data.get('class', '').strip()
    
    if not student_name or not class_name:
        if request.is_json:
            return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات'})
        flash('الرجاء إدخال جميع البيانات', 'error')
        return redirect(url_for('register'))
    
    if class_name not in CLASSES:
        if request.is_json:
            return jsonify({'success': False, 'message': 'الصف غير صحيح'})
        flash('الصف غير صحيح', 'error')
        return redirect(url_for('register'))
    
    success = db.add_student(class_name, student_name)
    
    if request.is_json:
        if success:
            return jsonify({'success': True, 'message': 'تم التسجيل بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'الطالب مسجل بالفعل'})
    else:
        if success:
            flash('تم التسجيل بنجاح', 'success')
        else:
            flash('الطالب مسجل بالفعل', 'error')
        return redirect(url_for('register'))

@app.route('/qr_code')
def qr_code():
    """Generate and display QR code"""
    # Get the base URL dynamically
    base_url = request.url_root.rstrip('/')
    
    # Check if we have a custom domain/IP in environment variables
    public_url = os.environ.get('PUBLIC_URL')
    if public_url:
        registration_url = f"{public_url}/register"
    else:
        # Use the dynamic URL generation
        registration_url = get_registration_url(base_url=base_url)
    
    # Generate QR code
    qr_image = generate_qr_code(registration_url, 400)
    
    # Convert to base64 for embedding
    img_buffer = io.BytesIO()
    qr_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('qr_code.html', 
                         qr_image=img_base64, 
                         registration_url=registration_url)

@app.route('/api/refresh')
def refresh_data():
    """API endpoint to get fresh data"""
    all_students = db.get_all_classes_with_students()
    
    grades = {
        'الرابع': [],
        'الخامس': [],
        'السادس': []
    }
    
    for class_name in CLASSES:
        students = all_students.get(class_name, [])
        class_info = {
            'name': class_name,
            'students': students,
            'count': len(students),
            'color': GRADE_COLORS.get(class_name.split()[0], '#3498db')
        }
        
        if 'الرابع' in class_name:
            grades['الرابع'].append(class_info)
        elif 'الخامس' in class_name:
            grades['الخامس'].append(class_info)
        elif 'السادس' in class_name:
            grades['السادس'].append(class_info)
    
    return jsonify({'success': True, 'grades': grades})

if __name__ == '__main__':
    # Enable debug mode and set host to allow external access
    app.run(debug=True, host='0.0.0.0', port=5002, threaded=True)
