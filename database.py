import json
import os
import fcntl
import time
from typing import Dict, List, Optional
from contextlib import contextmanager

class Database:
    def __init__(self, filename='school_data.json'):
        self.filename = filename
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize the database file if it doesn't exist"""
        if not os.path.exists(self.filename):
            initial_data = {
                'students': {},  # {class_name: [student_names]}
                'password': 'admin123'  # Default password
            }
            self._write_data(initial_data)
    
    @contextmanager
    def _file_lock(self, mode='r'):
        """Context manager for file locking"""
        max_retries = 10
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                file = open(self.filename, mode)
                # Acquire exclusive lock for writing, shared lock for reading
                lock_type = fcntl.LOCK_EX if 'w' in mode or '+' in mode else fcntl.LOCK_SH
                fcntl.flock(file.fileno(), lock_type | fcntl.LOCK_NB)
                yield file
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)
                file.close()
                return
            except IOError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception("Could not acquire file lock after multiple attempts")
            except Exception as e:
                if 'file' in locals():
                    file.close()
                raise e
    
    def _read_data(self) -> Dict:
        """Read data from the JSON file with locking"""
        with self._file_lock('r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {'students': {}, 'password': 'admin123'}
    
    def _write_data(self, data: Dict):
        """Write data to the JSON file with locking"""
        with self._file_lock('w') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    
    def add_student(self, class_name: str, student_name: str) -> bool:
        """Add a student to a class"""
        data = self._read_data()
        
        if class_name not in data['students']:
            data['students'][class_name] = []
        
        if student_name not in data['students'][class_name]:
            data['students'][class_name].append(student_name)
            self._write_data(data)
            return True
        return False
    
    def remove_student(self, class_name: str, student_name: str, password: str) -> tuple[bool, str]:
        """Remove a student from a class with password verification"""
        data = self._read_data()
        
        if data['password'] != password:
            return False, "كلمة المرور غير صحيحة"
        
        if class_name in data['students'] and student_name in data['students'][class_name]:
            data['students'][class_name].remove(student_name)
            self._write_data(data)
            return True, "تم حذف الطالب بنجاح"
        
        return False, "الطالب غير موجود"
    
    def get_students(self, class_name: str) -> List[str]:
        """Get all students in a class"""
        data = self._read_data()
        return data['students'].get(class_name, [])
    
    def get_all_classes_with_students(self) -> Dict[str, List[str]]:
        """Get all classes with their students"""
        data = self._read_data()
        return data['students']
    
    def update_password(self, old_password: str, new_password: str) -> bool:
        """Update the admin password"""
        data = self._read_data()
        
        if data['password'] != old_password:
            return False
        
        data['password'] = new_password
        self._write_data(data)
        return True
