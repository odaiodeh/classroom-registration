#!/usr/bin/env python3
"""
اختبار سريع لتشغيل التطبيق
Quick test to run the application
"""

print("🚀 بدء اختبار سريع للتطبيق...")

# Test 1: Import the main app
try:
    from app import app
    print("✅ تم استيراد التطبيق بنجاح")
except Exception as e:
    print(f"❌ خطأ في استيراد التطبيق: {e}")
    exit(1)

# Test 2: Test database
try:
    from database import Database
    db = Database('test_quick.json')
    db.add_student("الرابع أ", "اختبار سريع")
    students = db.get_students("الرابع أ")
    if students:
        print("✅ قاعدة البيانات تعمل بنجاح")
    import os
    if os.path.exists('test_quick.json'):
        os.remove('test_quick.json')
except Exception as e:
    print(f"❌ خطأ في قاعدة البيانات: {e}")

# Test 3: Test utils
try:
    from utils import reshape_arabic_text, CLASSES
    text = reshape_arabic_text("اختبار")
    if text and len(CLASSES) == 14:
        print("✅ الوظائف المساعدة تعمل بنجاح")
except Exception as e:
    print(f"❌ خطأ في الوظائف المساعدة: {e}")

print("\n🎯 لتشغيل التطبيق:")
print("1. python app.py")
print("2. افتح المتصفح: http://localhost:5002")
print("\n📱 أو جرب التطبيق مباشرة:")
print("python -c \"from app import app; app.run(debug=True, host='localhost', port=5002)\"")
