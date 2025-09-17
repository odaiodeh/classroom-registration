from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
import io
import base64
import os
import sys
import argparse
from database import Database
from utils import reshape_arabic_text, generate_qr_code, get_registration_url
from classes_manager import ClassesManager
import json

app = Flask(__name__)
app.secret_key = 'school_secret_key_2024'  # Change this in production

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='School Classes Management System')
    parser.add_argument('--config', '-c', 
                       default='classes.json',
                       help='Path to classes configuration file (default: classes.json)')
    parser.add_argument('--port', '-p', 
                       type=int, 
                       default=5000,
                       help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', 
                       default='127.0.0.1',
                       help='Host to run the server on (default: 127.0.0.1)')
    parser.add_argument('--debug', 
                       action='store_true',
                       help='Run in debug mode')
    return parser.parse_args()

# Initialize database
db = Database()

# Classes manager - will be initialized based on command line args
classes_manager = None

def init_classes_manager(config_file='classes.json'):
    """Initialize the classes manager with the specified config file"""
    global classes_manager
    classes_manager = ClassesManager(config_file=config_file)

# Initialize with default config if not running as main script
# This will be overridden if run with command line arguments
if classes_manager is None:
    init_classes_manager()

@app.route('/')
def home():
    """Home page with classroom cards"""
    all_students = db.get_all_classes_with_students()
    
    # Get classes configuration from classes manager
    classes_config = classes_manager.get_formatted_classes_for_display()
    
    # Organize classes by grade with student data
    grades = {}
    all_classes = []
    
    for grade_name, grade_classes in classes_config.items():
        grades[grade_name] = []
        for class_config in grade_classes:
            class_name = class_config['name']
            students = all_students.get(class_name, [])
            
            class_info = {
                'name': class_name,
                'students': students[:30],  # Limit to 30 for display
                'count': len(students),
                'color': class_config['color'],
                'code': class_config.get('code', ''),
                'type': class_config.get('type', 'general')
            }
            
            grades[grade_name].append(class_info)
            all_classes.append(class_info)
    
    # Get list of all class names for dropdowns
    classes_list = classes_manager.get_all_classes_list()
    
    # Get school settings for display
    school_settings = classes_manager.get_school_settings()
    
    # Calculate total students for initial display
    total_students = sum(len(students) for students in all_students.values())
    
    return render_template('home.html', grades=grades, classes=all_classes, classes_list=classes_list, school_settings=school_settings, total_students=total_students)

@app.route('/add_student', methods=['POST'])
def add_student():
    """Add a student to a class"""
    data = request.get_json()
    student_name = data.get('name', '').strip()
    class_name = data.get('class', '').strip()
    
    if not student_name or not class_name:
        return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات'})
    
    # Validate class name using classes manager
    all_classes = classes_manager.get_all_classes_list()
    if class_name not in all_classes:
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
    # Validate class name using classes manager
    all_classes = classes_manager.get_all_classes_list()
    if class_name not in all_classes:
        return jsonify({'success': False, 'message': 'الصف غير صحيح'})
    
    students = db.get_students(class_name)
    return jsonify({'success': True, 'students': students})

# New API endpoints for classes management

@app.route('/api/classes')
def api_get_all_classes():
    """Get all classes configuration"""
    try:
        return jsonify({
            'success': True,
            'classes': classes_manager.get_all_classes_list(),
            'grades': classes_manager.get_all_grades(),
            'formatted': classes_manager.get_formatted_classes_for_display()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/classes/grade/<grade_name>')
def api_get_classes_by_grade(grade_name):
    """Get classes for a specific grade"""
    try:
        classes = classes_manager.get_classes_by_grade(grade_name)
        return jsonify({
            'success': True,
            'grade': grade_name,
            'classes': classes
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/classes/info/<class_name>')
def api_get_class_info(class_name):
    """Get detailed information about a specific class"""
    try:
        class_info = classes_manager.get_class_info(class_name)
        if not class_info:
            return jsonify({'success': False, 'message': 'الصف غير موجود'})
        
        # Add student data
        students = db.get_students(class_name)
        class_info['students'] = students
        class_info['student_count'] = len(students)
        
        return jsonify({
            'success': True,
            'class_info': class_info
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/settings')
def api_get_settings():
    """Get school settings"""
    try:
        settings = classes_manager.get_school_settings()
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/total-students')
def api_get_total_students():
    """Get total number of students across all classes"""
    try:
        all_students = db.get_all_classes_with_students()
        total_count = sum(len(students) for students in all_students.values())
        return jsonify({
            'success': True,
            'total': total_count,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/students-data')
def api_get_students_data():
    """Get all students organized by categories - CLEAN AND SIMPLE"""
    try:
        # Get raw student data from database
        all_students = db.get_all_classes_with_students()
        
        # Get classes configuration 
        classes_config = classes_manager.get_formatted_classes_for_display()
        
        # Build clean response
        categories = {}
        total_students = 0
        
        for category_name, classes_list in classes_config.items():
            categories[category_name] = {
                'name': category_name,
                'classes': []
            }
            
            for class_config in classes_list:
                class_name = class_config['name']
                students = all_students.get(class_name, [])
                
                class_data = {
                    'name': class_name,
                    'students': students,
                    'count': len(students),
                    'color': class_config.get('color', '#3498db')
                }
                
                categories[category_name]['classes'].append(class_data)
                total_students += len(students)
        
        return jsonify({
            'success': True,
            'categories': categories,
            'total_students': total_students,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"ERROR in students-data API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug-count')
def api_debug_count():
    """Debug endpoint to show detailed count breakdown"""
    try:
        # Get raw database data
        all_students = db.get_all_classes_with_students()
        
        debug_info = {
            'raw_database_classes': {},
            'total_registrations': 0,
            'unique_students': set(),
            'class_breakdown': []
        }
        
        # Analyze each class in database
        for class_name, students in all_students.items():
            debug_info['raw_database_classes'][class_name] = {
                'students': students,
                'count': len(students)
            }
            debug_info['total_registrations'] += len(students)
            
            # Track unique students
            for student in students:
                debug_info['unique_students'].add(student.lower().strip())
            
            debug_info['class_breakdown'].append({
                'class': class_name,
                'students': students,
                'count': len(students)
            })
        
        # Convert set to list for JSON serialization
        debug_info['unique_students'] = list(debug_info['unique_students'])
        debug_info['unique_count'] = len(debug_info['unique_students'])
        
        return jsonify({
            'success': True,
            'debug': debug_info,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"ERROR in debug-count API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classes/add', methods=['POST'])
def api_add_class():
    """Add a new class to a grade"""
    try:
        data = request.get_json()
        grade_name = data.get('grade_name', '').strip()
        class_name = data.get('class_name', '').strip()
        class_code = data.get('class_code', '').strip()
        class_type = data.get('class_type', 'section').strip()
        
        if not grade_name or not class_name:
            return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات المطلوبة'})
        
        success = classes_manager.add_class_to_grade(grade_name, class_name, class_code, class_type)
        
        if success:
            return jsonify({'success': True, 'message': 'تم إضافة الصف بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في إضافة الصف'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/classes/remove', methods=['POST'])
def api_remove_class():
    """Remove a class from a grade"""
    try:
        data = request.get_json()
        grade_name = data.get('grade_name', '').strip()
        class_name = data.get('class_name', '').strip()
        
        if not grade_name or not class_name:
            return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات المطلوبة'})
        
        success = classes_manager.remove_class_from_grade(grade_name, class_name)
        
        if success:
            return jsonify({'success': True, 'message': 'تم حذف الصف بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في حذف الصف'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page for QR code access"""
    if request.method == 'GET':
        classes_list = classes_manager.get_all_classes_list()
        school_settings = classes_manager.get_school_settings()
        return render_template('register.html', classes=classes_list, school_settings=school_settings)
    
    # POST request - handle registration
    data = request.get_json() if request.is_json else request.form
    student_name = data.get('name', '').strip()
    class_name = data.get('class', '').strip()
    
    if not student_name or not class_name:
        if request.is_json:
            return jsonify({'success': False, 'message': 'الرجاء إدخال جميع البيانات'})
        flash('الرجاء إدخال جميع البيانات', 'error')
        return redirect(url_for('register'))
    
    # Validate class name using classes manager
    all_classes = classes_manager.get_all_classes_list()
    if class_name not in all_classes:
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
    
    school_settings = classes_manager.get_school_settings()
    return render_template('qr_code.html', 
                         qr_image=img_base64, 
                         registration_url=registration_url,
                         school_settings=school_settings)

@app.route('/clear_all_students', methods=['POST'])
def clear_all_students():
    """Clear all students from all classes with password protection"""
    try:
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if not password:
            return jsonify({'success': False, 'message': 'كلمة المرور مطلوبة'})
        
        # Verify password using database
        success, message = db.remove_student("dummy", "dummy", password)
        if not success and "كلمة المرور غير صحيحة" in message:
            return jsonify({'success': False, 'message': 'كلمة المرور غير صحيحة'})
        
        # Clear all students from all classes
        success = db.clear_all_students()
        
        if success:
            # Log the action
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] ALL STUDENTS CLEARED by admin")
            
            return jsonify({'success': True, 'message': 'تم حذف جميع الطلاب بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل في حذف الطلاب'})
            
    except Exception as e:
        print(f"Error in clear_all_students: {str(e)}")
        return jsonify({'success': False, 'message': f'خطأ في النظام: {str(e)}'}), 500

@app.route('/api/refresh')
def refresh_data():
    """API endpoint to get fresh data for live updates"""
    try:
        all_students = db.get_all_classes_with_students()
        
        # Get classes configuration from classes manager
        classes_config = classes_manager.get_formatted_classes_for_display()
        
        # Organize classes by grade with student data
        grades = {}
        
        for grade_name, grade_classes in classes_config.items():
            grades[grade_name] = []
            for class_config in grade_classes:
                class_name = class_config['name']
                students = all_students.get(class_name, [])
                
                class_info = {
                    'name': class_name,
                    'students': students[:30],  # Limit to 30 for display
                    'count': len(students),
                    'color': class_config['color'],
                    'code': class_config.get('code', ''),
                    'type': class_config.get('type', 'general')
                }
                
                grades[grade_name].append(class_info)
        
        return jsonify({'success': True, 'grades': grades})
        
    except Exception as e:
        print(f"Error in refresh_data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize classes manager with specified config file
    init_classes_manager(args.config)
    
    # Print startup information
    print(f"🚀 Starting School Registration Server...")
    print(f"📁 Config file: {args.config}")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🐛 Debug: {args.debug}")
    print(f"🌐 Local URL: http://localhost:{args.port}")
    print(f"🌐 Network URL: http://{args.host}:{args.port}")
    print(f"📱 QR Code: http://localhost:{args.port}/qr_code")
    print(f"📝 Registration: http://localhost:{args.port}/register")
    print("="*50)
    
    # Enable debug mode and set host to allow external access
    try:
        app.run(debug=args.debug, host=args.host, port=args.port, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Error: Port {args.port} is already in use!")
            print(f"💡 Try a different port: python app.py --port {args.port + 1}")
            sys.exit(1)
        else:
            raise e
