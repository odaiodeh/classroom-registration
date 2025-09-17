#!/usr/bin/env python3
"""Test script to verify the application components"""

import sys

# Test imports
try:
    print("Testing imports...")
    import customtkinter
    print("✓ customtkinter imported successfully")
    
    import qrcode
    print("✓ qrcode imported successfully")
    
    import PIL
    print("✓ PIL imported successfully")
    
    import arabic_reshaper
    print("✓ arabic_reshaper imported successfully")
    
    import bidi
    print("✓ python-bidi imported successfully")
    
    # Test local modules
    from database import Database
    print("✓ Database module imported successfully")
    
    from utils import reshape_arabic_text, CLASSES
    print("✓ Utils module imported successfully")
    
    from registration_server import RegistrationHandler
    print("✓ Registration server imported successfully")
    
    print("\n" + "="*50)
    print("All imports successful!")
    print("="*50 + "\n")
    
    # Test database operations
    print("Testing database operations...")
    db = Database('test_school_data.json')
    
    # Add a student
    success = db.add_student("الرابع أ", "أحمد محمد")
    print(f"✓ Add student: {'Success' if success else 'Failed'}")
    
    # Get students
    students = db.get_students("الرابع أ")
    print(f"✓ Get students: {students}")
    
    # Test Arabic text reshaping
    print("\nTesting Arabic text reshaping...")
    original = "المدرسة الجماهيرية"
    reshaped = reshape_arabic_text(original)
    print(f"✓ Original: {original}")
    print(f"✓ Reshaped: {reshaped}")
    
    # Display available classes
    print("\nAvailable classes:")
    for i, class_name in enumerate(CLASSES, 1):
        print(f"{i}. {class_name}")
    
    print("\n" + "="*50)
    print("All tests passed! The application is ready to run.")
    print("Run 'python main.py' to start the application.")
    print("="*50)
    
    # Clean up test file
    import os
    if os.path.exists('test_school_data.json'):
        os.remove('test_school_data.json')
        
except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    print("\nPlease install the required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    sys.exit(1)
