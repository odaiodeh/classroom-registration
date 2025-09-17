#!/usr/bin/env python3
"""
Comprehensive Test Suite for School Registration Web Application
المدرسة الجماهيرية بئر الأمير - الناصرة

This script tests all functionality of the Flask web application.
Run this before using the application to ensure everything works correctly.
"""

import sys
import os
import json
import time
import threading
import requests
from io import StringIO
import tempfile

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(test_name):
    print(f"{Colors.YELLOW}🧪 {test_name}...{Colors.END}", end=' ')

def print_pass(message="PASS"):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_fail(message="FAIL"):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

class WebAppTester:
    def __init__(self):
        self.base_url = "http://localhost:5002"
        self.app_process = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print_header("مجموعة اختبارات تطبيق المدرسة الجماهيرية")
        print_info("بدء اختبار جميع وظائف التطبيق...")
        
        # Test 1: Import Tests
        self.test_imports()
        
        # Test 2: Database Tests
        self.test_database_operations()
        
        # Test 3: Utils Tests
        self.test_utils()
        
        # Test 4: Flask App Structure
        self.test_flask_structure()
        
        # Test 5: Start Flask App
        if self.start_flask_app():
            # Test 6: Web Endpoints
            self.test_web_endpoints()
            
            # Test 7: API Functionality
            self.test_api_functionality()
            
            # Test 8: QR Code Generation
            self.test_qr_code()
            
            # Test 9: Frontend Functionality
            self.test_frontend_elements()
            
            # Stop Flask App
            self.stop_flask_app()
        
        # Test Results Summary
        self.print_test_summary()
        
    def test_imports(self):
        """Test all required imports"""
        print_header("اختبار استيراد المكتبات")
        
        imports_to_test = [
            ("Flask", "flask"),
            ("qrcode", "qrcode"),
            ("PIL (Pillow)", "PIL"),
            ("arabic_reshaper", "arabic_reshaper"),
            ("python-bidi", "bidi"),
            ("Werkzeug", "werkzeug")
        ]
        
        for name, module in imports_to_test:
            print_test(f"استيراد {name}")
            try:
                __import__(module)
                print_pass()
                self.test_results["passed"] += 1
            except ImportError as e:
                print_fail(f"فشل - {e}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"Import error: {name} - {e}")
        
        # Test local modules
        local_modules = [
            ("database", "Database"),
            ("utils", "CLASSES, reshape_arabic_text"),
            ("app", "Flask app")
        ]
        
        for module, desc in local_modules:
            print_test(f"استيراد {desc}")
            try:
                if module == "database":
                    from database import Database
                elif module == "utils":
                    from utils import CLASSES, reshape_arabic_text, generate_qr_code
                elif module == "app":
                    from app import app
                print_pass()
                self.test_results["passed"] += 1
            except Exception as e:
                print_fail(f"فشل - {e}")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"Local import error: {module} - {e}")
    
    def test_database_operations(self):
        """Test database functionality"""
        print_header("اختبار قاعدة البيانات")
        
        try:
            from database import Database
            
            # Create test database
            test_db_file = "test_school_data.json"
            db = Database(test_db_file)
            
            # Test 1: Add student
            print_test("إضافة طالب")
            success = db.add_student("الرابع أ", "أحمد محمد السعيد")
            if success:
                print_pass()
                self.test_results["passed"] += 1
            else:
                print_fail()
                self.test_results["failed"] += 1
            
            # Test 2: Add duplicate student
            print_test("إضافة طالب مكرر")
            success = db.add_student("الرابع أ", "أحمد محمد السعيد")
            if not success:  # Should fail for duplicate
                print_pass("رُفض بنجاح - لا يمكن إضافة طالب مكرر")
                self.test_results["passed"] += 1
            else:
                print_fail("لم يرفض الطالب المكرر")
                self.test_results["failed"] += 1
            
            # Test 3: Get students
            print_test("جلب قائمة الطلاب")
            students = db.get_students("الرابع أ")
            if len(students) == 1 and students[0] == "أحمد محمد السعيد":
                print_pass(f"عدد الطلاب: {len(students)}")
                self.test_results["passed"] += 1
            else:
                print_fail(f"عدد خاطئ: {len(students)}")
                self.test_results["failed"] += 1
            
            # Test 4: Remove student with correct password
            print_test("حذف طالب بكلمة مرور صحيحة")
            success, message = db.remove_student("الرابع أ", "أحمد محمد السعيد", "admin123")
            if success:
                print_pass(f"تم الحذف: {message}")
                self.test_results["passed"] += 1
            else:
                print_fail(f"فشل الحذف: {message}")
                self.test_results["failed"] += 1
            
            # Test 5: Remove student with wrong password
            db.add_student("الرابع أ", "فاطمة علي")
            print_test("حذف طالب بكلمة مرور خاطئة")
            success, message = db.remove_student("الرابع أ", "فاطمة علي", "wrongpassword")
            if not success:
                print_pass(f"رُفض بنجاح: {message}")
                self.test_results["passed"] += 1
            else:
                print_fail("لم يرفض كلمة المرور الخاطئة")
                self.test_results["failed"] += 1
            
            # Test 6: Get all classes
            print_test("جلب جميع الصفوف")
            all_classes = db.get_all_classes_with_students()
            if isinstance(all_classes, dict):
                print_pass(f"عدد الصفوف: {len(all_classes)}")
                self.test_results["passed"] += 1
            else:
                print_fail("فشل في جلب البيانات")
                self.test_results["failed"] += 1
            
            # Clean up
            if os.path.exists(test_db_file):
                os.remove(test_db_file)
                
        except Exception as e:
            print_fail(f"خطأ في اختبار قاعدة البيانات: {e}")
            self.test_results["failed"] += 6
            self.test_results["errors"].append(f"Database test error: {e}")
    
    def test_utils(self):
        """Test utility functions"""
        print_header("اختبار الوظائف المساعدة")
        
        try:
            from utils import reshape_arabic_text, generate_qr_code, CLASSES, COLORS
            
            # Test 1: Arabic text reshaping
            print_test("تنسيق النص العربي")
            text = "المدرسة الجماهيرية"
            reshaped = reshape_arabic_text(text)
            if reshaped:
                print_pass(f"النص الأصلي: {text}")
                print_info(f"النص المنسق: {reshaped}")
                self.test_results["passed"] += 1
            else:
                print_fail()
                self.test_results["failed"] += 1
            
            # Test 2: QR Code generation
            print_test("إنشاء رمز QR")
            qr_image = generate_qr_code("http://test.com", 200)
            if qr_image and hasattr(qr_image, 'size'):
                print_pass(f"حجم الصورة: {qr_image.size}")
                self.test_results["passed"] += 1
            else:
                print_fail()
                self.test_results["failed"] += 1
            
            # Test 3: Classes list
            print_test("قائمة الصفوف")
            if len(CLASSES) == 14:  # Expected number of classes
                print_pass(f"عدد الصفوف: {len(CLASSES)}")
                print_info("الصفوف المتاحة:")
                for i, class_name in enumerate(CLASSES[:5], 1):
                    print_info(f"  {i}. {class_name}")
                if len(CLASSES) > 5:
                    print_info(f"  ... و {len(CLASSES)-5} صفوف أخرى")
                self.test_results["passed"] += 1
            else:
                print_fail(f"عدد خاطئ: {len(CLASSES)}")
                self.test_results["failed"] += 1
            
            # Test 4: Colors configuration
            print_test("إعدادات الألوان")
            if isinstance(COLORS, dict) and 'primary' in COLORS:
                print_pass(f"عدد الألوان: {len(COLORS)}")
                self.test_results["passed"] += 1
            else:
                print_fail()
                self.test_results["failed"] += 1
                
        except Exception as e:
            print_fail(f"خطأ في اختبار الوظائف المساعدة: {e}")
            self.test_results["failed"] += 4
            self.test_results["errors"].append(f"Utils test error: {e}")
    
    def test_flask_structure(self):
        """Test Flask application structure"""
        print_header("اختبار هيكل تطبيق Flask")
        
        try:
            from app import app
            
            # Test 1: Flask app creation
            print_test("إنشاء تطبيق Flask")
            if app and hasattr(app, 'route'):
                print_pass()
                self.test_results["passed"] += 1
            else:
                print_fail()
                self.test_results["failed"] += 1
            
            # Test 2: Routes registration
            print_test("تسجيل المسارات")
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            expected_routes = ['/', '/add_student', '/remove_student', '/register', '/qr_code', '/api/refresh']
            
            missing_routes = [route for route in expected_routes if route not in routes]
            if not missing_routes:
                print_pass(f"عدد المسارات: {len(routes)}")
                self.test_results["passed"] += 1
            else:
                print_fail(f"مسارات مفقودة: {missing_routes}")
                self.test_results["failed"] += 1
            
            # Test 3: Templates directory
            print_test("مجلد القوالب")
            templates_dir = os.path.join(os.getcwd(), 'templates')
            if os.path.exists(templates_dir):
                template_files = os.listdir(templates_dir)
                expected_templates = ['base.html', 'home.html', 'register.html', 'qr_code.html']
                missing_templates = [t for t in expected_templates if t not in template_files]
                
                if not missing_templates:
                    print_pass(f"عدد القوالب: {len(template_files)}")
                    self.test_results["passed"] += 1
                else:
                    print_fail(f"قوالب مفقودة: {missing_templates}")
                    self.test_results["failed"] += 1
            else:
                print_fail("مجلد القوالب غير موجود")
                self.test_results["failed"] += 1
                
        except Exception as e:
            print_fail(f"خطأ في اختبار Flask: {e}")
            self.test_results["failed"] += 3
            self.test_results["errors"].append(f"Flask structure test error: {e}")
    
    def start_flask_app(self):
        """Start Flask application for testing"""
        print_header("تشغيل تطبيق Flask")
        
        try:
            import subprocess
            import time
            
            print_test("تشغيل الخادم")
            
            # Start Flask app in background
            self.app_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for server to start
            print_info("انتظار بدء تشغيل الخادم...")
            time.sleep(5)  # Increased wait time
            
            # Test if server is running with multiple attempts
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    print_info(f"محاولة الاتصال {attempt + 1}/{max_attempts}...")
                    response = requests.get(f"{self.base_url}/", timeout=10)
                    if response.status_code == 200:
                        print_pass("الخادم يعمل بنجاح")
                        self.test_results["passed"] += 1
                        return True
                    elif response.status_code == 403:
                        print_warning(f"403 Forbidden - قد تكون مشكلة في الصلاحيات")
                        if attempt < max_attempts - 1:
                            print_info("محاولة مرة أخرى...")
                            time.sleep(2)
                            continue
                    else:
                        print_warning(f"رمز استجابة: {response.status_code}")
                        if attempt < max_attempts - 1:
                            time.sleep(2)
                            continue
                except requests.exceptions.ConnectionError:
                    if attempt < max_attempts - 1:
                        print_info("الخادم لم يبدأ بعد، انتظار...")
                        time.sleep(3)
                        continue
                    else:
                        print_fail("فشل الاتصال بالخادم")
                except requests.exceptions.RequestException as e:
                    print_fail(f"خطأ في الطلب: {e}")
                    break
            
            # If we get here, all attempts failed
            print_fail("فشل في تشغيل الخادم بعد عدة محاولات")
            self.test_results["failed"] += 1
            return False
                
        except Exception as e:
            print_fail(f"خطأ في تشغيل الخادم: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Flask startup error: {e}")
            return False
    
    def test_web_endpoints(self):
        """Test web endpoints"""
        print_header("اختبار نقاط النهاية")
        
        endpoints_to_test = [
            ("/", "الصفحة الرئيسية"),
            ("/register", "صفحة التسجيل"),
            ("/qr_code", "صفحة رمز QR"),
            ("/api/refresh", "API تحديث البيانات")
        ]
        
        for endpoint, description in endpoints_to_test:
            print_test(f"اختبار {description}")
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print_pass(f"حالة: {response.status_code}")
                    self.test_results["passed"] += 1
                else:
                    print_fail(f"حالة: {response.status_code}")
                    self.test_results["failed"] += 1
            except Exception as e:
                print_fail(f"خطأ: {e}")
                self.test_results["failed"] += 1
    
    def test_api_functionality(self):
        """Test API endpoints functionality"""
        print_header("اختبار وظائف API")
        
        # Test 1: Add student API
        print_test("API إضافة طالب")
        try:
            data = {
                "name": "سارة أحمد الزهراني",
                "class": "الرابع أ"
            }
            response = requests.post(
                f"{self.base_url}/add_student",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print_pass("تمت الإضافة بنجاح")
                    self.test_results["passed"] += 1
                else:
                    print_fail(f"فشل: {result.get('message')}")
                    self.test_results["failed"] += 1
            else:
                print_fail(f"رمز الاستجابة: {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            print_fail(f"خطأ: {e}")
            self.test_results["failed"] += 1
        
        # Test 2: Get students API
        print_test("API جلب الطلاب")
        try:
            response = requests.get(
                f"{self.base_url}/get_students/الرابع أ",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    students = result.get('students', [])
                    print_pass(f"عدد الطلاب: {len(students)}")
                    self.test_results["passed"] += 1
                else:
                    print_fail(f"فشل: {result.get('message')}")
                    self.test_results["failed"] += 1
            else:
                print_fail(f"رمز الاستجابة: {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            print_fail(f"خطأ: {e}")
            self.test_results["failed"] += 1
        
        # Test 3: Remove student API (with wrong password)
        print_test("API حذف طالب (كلمة مرور خاطئة)")
        try:
            data = {
                "name": "سارة أحمد الزهراني",
                "class": "الرابع أ",
                "password": "wrongpassword"
            }
            response = requests.post(
                f"{self.base_url}/remove_student",
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if not result.get('success'):  # Should fail
                    print_pass("رُفض بنجاح - كلمة مرور خاطئة")
                    self.test_results["passed"] += 1
                else:
                    print_fail("لم يرفض كلمة المرور الخاطئة")
                    self.test_results["failed"] += 1
            else:
                print_fail(f"رمز الاستجابة: {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            print_fail(f"خطأ: {e}")
            self.test_results["failed"] += 1
    
    def test_qr_code(self):
        """Test QR code functionality"""
        print_header("اختبار رمز QR")
        
        print_test("إنشاء رمز QR")
        try:
            response = requests.get(f"{self.base_url}/qr_code", timeout=10)
            if response.status_code == 200:
                content = response.text
                if "data:image/png;base64," in content:
                    print_pass("تم إنشاء رمز QR بنجاح")
                    self.test_results["passed"] += 1
                else:
                    print_fail("لم يتم العثور على رمز QR في الصفحة")
                    self.test_results["failed"] += 1
            else:
                print_fail(f"رمز الاستجابة: {response.status_code}")
                self.test_results["failed"] += 1
        except Exception as e:
            print_fail(f"خطأ: {e}")
            self.test_results["failed"] += 1
    
    def test_frontend_elements(self):
        """Test frontend elements"""
        print_header("اختبار عناصر الواجهة")
        
        pages_to_test = [
            ("/", ["المدرسة الجماهيرية", "بئر الأمير", "الناصرة"]),
            ("/register", ["تسجيل طالب", "اسم الطالب", "الصف"]),
            ("/qr_code", ["رمز QR", "التسجيل", "امسح"])
        ]
        
        for url, expected_texts in pages_to_test:
            print_test(f"اختبار محتوى الصفحة {url}")
            try:
                response = requests.get(f"{self.base_url}{url}", timeout=10)
                if response.status_code == 200:
                    content = response.text
                    missing_texts = [text for text in expected_texts if text not in content]
                    
                    if not missing_texts:
                        print_pass("جميع العناصر موجودة")
                        self.test_results["passed"] += 1
                    else:
                        print_fail(f"عناصر مفقودة: {missing_texts}")
                        self.test_results["failed"] += 1
                else:
                    print_fail(f"رمز الاستجابة: {response.status_code}")
                    self.test_results["failed"] += 1
            except Exception as e:
                print_fail(f"خطأ: {e}")
                self.test_results["failed"] += 1
    
    def stop_flask_app(self):
        """Stop Flask application"""
        print_header("إيقاف تطبيق Flask")
        
        if self.app_process:
            print_test("إيقاف الخادم")
            self.app_process.terminate()
            self.app_process.wait()
            print_pass("تم إيقاف الخادم")
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print_header("ملخص نتائج الاختبار")
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Colors.BOLD}إجمالي الاختبارات: {total_tests}{Colors.END}")
        print(f"{Colors.GREEN}نجح: {self.test_results['passed']}{Colors.END}")
        print(f"{Colors.RED}فشل: {self.test_results['failed']}{Colors.END}")
        print(f"{Colors.BOLD}معدل النجاح: {success_rate:.1f}%{Colors.END}")
        
        if success_rate >= 90:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ممتاز! التطبيق جاهز للاستخدام{Colors.END}")
        elif success_rate >= 75:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ جيد - هناك بعض المشاكل البسيطة{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ يحتاج إصلاح - مشاكل كثيرة{Colors.END}")
        
        if self.test_results["errors"]:
            print(f"\n{Colors.RED}{Colors.BOLD}تفاصيل الأخطاء:{Colors.END}")
            for i, error in enumerate(self.test_results["errors"], 1):
                print(f"{Colors.RED}{i}. {error}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{Colors.BLUE}تعليمات التشغيل:{Colors.END}")
        print(f"{Colors.WHITE}1. pip install -r requirements.txt{Colors.END}")
        print(f"{Colors.WHITE}2. python app.py{Colors.END}")
        print(f"{Colors.WHITE}3. افتح المتصفح: http://localhost:5002{Colors.END}")
        
        print(f"\n{Colors.CYAN}رابط التسجيل عبر QR: http://localhost:5002/register{Colors.END}")
        print(f"{Colors.CYAN}رابط عرض رمز QR: http://localhost:5002/qr_code{Colors.END}")

def main():
    """Main function to run all tests"""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 70)
    print("اختبار شامل لتطبيق المدرسة الجماهيرية بئر الأمير - الناصرة".center(70))
    print("Comprehensive Test Suite for School Registration App".center(70))
    print("=" * 70)
    print(f"{Colors.END}")
    
    tester = WebAppTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}تم إيقاف الاختبار بواسطة المستخدم{Colors.END}")
        if tester.app_process:
            tester.stop_flask_app()
    except Exception as e:
        print(f"\n{Colors.RED}خطأ غير متوقع: {e}{Colors.END}")
        if tester.app_process:
            tester.stop_flask_app()

if __name__ == "__main__":
    main()
