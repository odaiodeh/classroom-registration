"""
Classes Configuration Manager
Handles loading and managing school classes configuration
"""

import json
import os
from typing import Dict, List, Any

class ClassesManager:
    def __init__(self, config_file='classes.json'):
        self.config_file = config_file
        self.classes_data = self.load_classes()
    
    def load_classes(self) -> Dict[str, Any]:
        """Load classes configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Return default configuration if file doesn't exist
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading classes config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Return default classes configuration"""
        return {
            "grades": {
                "طبقة الروابع": {
                    "name": "طبقة الروابع",
                    "color": "linear-gradient(135deg, #3498db 0%, #2980b9 100%)",
                    "classes": [
                        {"name": "الرابع \"أ\"", "code": "4-a", "type": "section"},
                        {"name": "الرابع \"ب\"", "code": "4-b", "type": "section"},
                        {"name": "الرابع \"ج\"", "code": "4-c", "type": "section"},
                        {"name": "الرابع \"د\"", "code": "4-d", "type": "section"},
                        {"name": "الرابع \"هـ\"", "code": "4-e", "type": "section"}
                    ]
                },
                "طبقة الخوامس": {
                    "name": "طبقة الخوامس",
                    "color": "linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%)",
                    "classes": [
                        {"name": "الخامس \"أ\"", "code": "5-a", "type": "section"},
                        {"name": "الخامس \"ب\"", "code": "5-b", "type": "section"},
                        {"name": "الخامس \"ج\"", "code": "5-c", "type": "section"},
                        {"name": "الخامس \"د\"", "code": "5-d", "type": "section"}
                    ]
                },
                "طبقة السوادس": {
                    "name": "طبقة السوادس",
                    "color": "linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)",
                    "classes": [
                        {"name": "السادس \"أ\"", "code": "6-a", "type": "section"},
                        {"name": "السادس \"ب\"", "code": "6-b", "type": "section"},
                        {"name": "السادس \"ج\"", "code": "6-c", "type": "section"},
                        {"name": "السادس \"د\"", "code": "6-d", "type": "section"},
                        {"name": "السادس \"هـ\"", "code": "6-e", "type": "section"}
                    ]
                }
            },
            "settings": {
                "school_name": "المدرسة الجماهيرية بئر الأمير - الناصرة",
                "event_title": "اجتماع أهالي طلاب الصفوف الثالثة وحتى السادسة",
                "default_password": "admin123",
                "texts": {
                    "registration_welcome": "أهلاً وسهلاً بكم في تسجيل الحضور",
                    "registration_instructions": "يرجى إدخال اسم الطالب واختيار الصف",
                    "student_name_label": "اسم الطالب",
                    "class_name_label": "الصف",
                    "register_button": "تسجيل الحضور",
                    "qr_code_title": "رمز QR للتسجيل",
                    "qr_code_instructions": "امسح هذا الرمز للوصول إلى صفحة التسجيل",
                    "management_title": "إدارة الطلاب",
                    "add_student": "إضافة طالب جديد",
                    "remove_student": "حذف طالب",
                    "refresh_data": "تحديث البيانات",
                    "class_selection": "اختيار الصف",
                    "student_list": "قائمة الطلاب",
                    "no_students": "لا يوجد طلاب في هذا الصف",
                    "password_required": "كلمة المرور مطلوبة لحذف الطلاب",
                    "total_students": "إجمالي الطلاب المسجلين",
                    "students_count": "طالب",
                    "success_messages": {
                        "student_added": "تم إضافة الطالب بنجاح",
                        "student_removed": "تم حذف الطالب بنجاح",
                        "registration_success": "تم التسجيل بنجاح"
                    },
                    "error_messages": {
                        "invalid_class": "الصف غير صحيح",
                        "missing_data": "الرجاء إدخال جميع البيانات المطلوبة",
                        "wrong_password": "كلمة المرور غير صحيحة",
                        "student_exists": "الطالب مسجل بالفعل",
                        "connection_error": "خطأ في الاتصال بالخادم"
                    }
                }
            }
        }
    
    def get_all_grades(self) -> Dict[str, Any]:
        """Get all grades configuration"""
        return self.classes_data.get('grades', {})
    
    def get_all_classes_list(self) -> List[str]:
        """Get a flat list of all class names"""
        classes = []
        for grade_data in self.classes_data.get('grades', {}).values():
            for class_info in grade_data.get('classes', []):
                classes.append(class_info['name'])
        return classes
    
    def get_classes_by_grade(self, grade_name: str) -> List[Dict[str, str]]:
        """Get all classes for a specific grade"""
        grade_data = self.classes_data.get('grades', {}).get(grade_name, {})
        return grade_data.get('classes', [])
    
    def get_class_info(self, class_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific class"""
        for grade_data in self.classes_data.get('grades', {}).values():
            for class_info in grade_data.get('classes', []):
                if class_info['name'] == class_name:
                    return {
                        **class_info,
                        'grade_color': grade_data.get('color', ''),
                        'grade_name': grade_data.get('name', '')
                    }
        return {}
    
    def get_formatted_classes_for_display(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get classes formatted for UI display"""
        formatted = {}
        for grade_name, grade_data in self.classes_data.get('grades', {}).items():
            formatted[grade_name] = []
            for class_info in grade_data.get('classes', []):
                formatted[grade_name].append({
                    'name': class_info['name'],
                    'code': class_info.get('code', ''),
                    'type': class_info.get('type', 'general'),
                    'color': grade_data.get('color', ''),
                    'students': [],  # Will be populated from database
                    'count': 0       # Will be populated from database
                })
        return formatted
    
    def get_school_settings(self) -> Dict[str, str]:
        """Get school configuration settings"""
        return self.classes_data.get('settings', {})
    
    def save_classes(self) -> bool:
        """Save current classes configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.classes_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving classes config: {e}")
            return False
    
    def add_class_to_grade(self, grade_name: str, class_name: str, class_code: str = None, class_type: str = "section") -> bool:
        """Add a new class to a specific grade"""
        try:
            if grade_name not in self.classes_data.get('grades', {}):
                return False
            
            if not class_code:
                class_code = class_name.lower().replace(' ', '-').replace('"', '')
            
            new_class = {
                "name": class_name,
                "code": class_code,
                "type": class_type
            }
            
            self.classes_data['grades'][grade_name]['classes'].append(new_class)
            return self.save_classes()
        except Exception as e:
            print(f"Error adding class: {e}")
            return False
    
    def remove_class_from_grade(self, grade_name: str, class_name: str) -> bool:
        """Remove a class from a specific grade"""
        try:
            if grade_name not in self.classes_data.get('grades', {}):
                return False
            
            classes = self.classes_data['grades'][grade_name]['classes']
            self.classes_data['grades'][grade_name]['classes'] = [
                c for c in classes if c['name'] != class_name
            ]
            return self.save_classes()
        except Exception as e:
            print(f"Error removing class: {e}")
            return False

# Global instance
classes_manager = ClassesManager()
