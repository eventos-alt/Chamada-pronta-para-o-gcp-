#!/usr/bin/env python3
"""
Backend API Testing for Sistema de Controle de Presença - IOS
Tests all endpoints with proper authentication and data validation
"""

import requests
import sys
import json
from datetime import datetime, date, timedelta

class IOSAPITester:
    def __init__(self, base_url="https://classchecker-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.instructor_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED {details}")
        else:
            print(f"❌ {name} - FAILED {details}")
        return success

    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            return success, response.json() if response.content else {}, response.status_code
            
        except Exception as e:
            return False, {"error": str(e)}, 0

    def test_system_initialization(self):
        """Test system initialization endpoint"""
        print("\n🔧 Testing System Initialization...")
        success, response, status = self.make_request('POST', 'init', expected_status=200)
        return self.log_test("System Initialization", success, f"Status: {status}")

    def test_admin_login(self):
        """Test admin login"""
        print("\n🔐 Testing Authentication...")
        login_data = {
            "email": "admin@ios.com.br",
            "senha": "admin123"
        }
        
        success, response, status = self.make_request('POST', 'auth/login', login_data)
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.test_data['admin_user'] = response['user']
            return self.log_test("Admin Login", True, f"Token received, User: {response['user']['nome']}")
        else:
            return self.log_test("Admin Login", False, f"Status: {status}, Response: {response}")

    def test_instructor_login(self):
        """Test instructor login"""
        login_data = {
            "email": "instrutor@ios.com.br",
            "senha": "instrutor123"
        }
        
        success, response, status = self.make_request('POST', 'auth/login', login_data)
        if success and 'access_token' in response:
            self.instructor_token = response['access_token']
            self.test_data['instructor_user'] = response['user']
            return self.log_test("Instructor Login", True, f"Token received, User: {response['user']['nome']}")
        else:
            return self.log_test("Instructor Login", False, f"Status: {status}, Response: {response}")

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        print("\n📊 Testing Dashboard Stats...")
        success, response, status = self.make_request('GET', 'dashboard/stats', token=self.admin_token)
        
        if success:
            expected_keys = ['total_unidades', 'total_cursos', 'total_alunos', 'total_turmas']
            has_keys = all(key in response for key in expected_keys)
            details = f"Units: {response.get('total_unidades', 0)}, Courses: {response.get('total_cursos', 0)}, Classes: {response.get('total_turmas', 0)}, Students: {response.get('total_alunos', 0)}"
            return self.log_test("Dashboard Stats", has_keys, details)
        else:
            return self.log_test("Dashboard Stats", False, f"Status: {status}")

    def test_units_endpoints(self):
        """Test units CRUD operations"""
        print("\n🏢 Testing Units Endpoints...")
        
        # Get units
        success, response, status = self.make_request('GET', 'units', token=self.admin_token)
        if success and isinstance(response, list):
            self.test_data['units'] = response
            self.log_test("Get Units", True, f"Found {len(response)} units")
        else:
            self.log_test("Get Units", False, f"Status: {status}")
            return False

        # Create new unit
        new_unit = {
            "nome": "Unidade Teste",
            "endereco": "Rua Teste, 123",
            "telefone": "(11) 9999-9999",
            "responsavel": "Responsável Teste"
        }
        
        success, response, status = self.make_request('POST', 'units', new_unit, token=self.admin_token, expected_status=200)
        if success and 'id' in response:
            self.test_data['test_unit_id'] = response['id']
            return self.log_test("Create Unit", True, f"Created unit with ID: {response['id']}")
        else:
            return self.log_test("Create Unit", False, f"Status: {status}, Response: {response}")

    def test_courses_endpoints(self):
        """Test courses CRUD operations"""
        print("\n📚 Testing Courses Endpoints...")
        
        # Get courses
        success, response, status = self.make_request('GET', 'courses', token=self.admin_token)
        if success and isinstance(response, list):
            self.test_data['courses'] = response
            self.log_test("Get Courses", True, f"Found {len(response)} courses")
        else:
            self.log_test("Get Courses", False, f"Status: {status}")
            return False

        # Create new course
        new_course = {
            "nome": "Curso Teste",
            "descricao": "Curso para testes automatizados",
            "carga_horaria": 40,
            "categoria": "Teste"
        }
        
        success, response, status = self.make_request('POST', 'courses', new_course, token=self.admin_token, expected_status=200)
        if success and 'id' in response:
            self.test_data['test_course_id'] = response['id']
            return self.log_test("Create Course", True, f"Created course with ID: {response['id']}")
        else:
            return self.log_test("Create Course", False, f"Status: {status}, Response: {response}")

    def test_students_endpoints(self):
        """Test students CRUD operations"""
        print("\n👨‍🎓 Testing Students Endpoints...")
        
        # Get students
        success, response, status = self.make_request('GET', 'students', token=self.admin_token)
        if success and isinstance(response, list):
            self.test_data['students'] = response
            self.log_test("Get Students", True, f"Found {len(response)} students")
        else:
            self.log_test("Get Students", False, f"Status: {status}")
            return False

        # Create new student
        new_student = {
            "nome": "Aluno Teste",
            "cpf": "12345678901",
            "email": "aluno.teste@email.com",
            "telefone": "(11) 9999-8888"
        }
        
        success, response, status = self.make_request('POST', 'students', new_student, token=self.admin_token, expected_status=200)
        if success and 'id' in response:
            self.test_data['test_student_id'] = response['id']
            return self.log_test("Create Student", True, f"Created student with ID: {response['id']}")
        else:
            return self.log_test("Create Student", False, f"Status: {status}, Response: {response}")

    def test_classes_endpoints(self):
        """Test classes CRUD operations"""
        print("\n🎓 Testing Classes Endpoints...")
        
        # Get classes
        success, response, status = self.make_request('GET', 'classes', token=self.admin_token)
        if success and isinstance(response, list):
            self.test_data['classes'] = response
            self.log_test("Get Classes", True, f"Found {len(response)} classes")
            
            # Test getting students for first class
            if response:
                class_id = response[0]['id']
                success2, students_response, status2 = self.make_request('GET', f'classes/{class_id}/students', token=self.admin_token)
                if success2:
                    self.log_test("Get Class Students", True, f"Found {len(students_response)} students in class")
                else:
                    self.log_test("Get Class Students", False, f"Status: {status2}")
        else:
            self.log_test("Get Classes", False, f"Status: {status}")
            return False

        # Create new class (requires existing units, courses, and instructors)
        if self.test_data.get('units') and self.test_data.get('courses'):
            today = date.today()
            end_date = today + timedelta(days=90)
            
            new_class = {
                "nome": "Turma Teste",
                "unidade_id": self.test_data['units'][0]['id'],
                "curso_id": self.test_data['courses'][0]['id'],
                "instrutor_id": self.test_data['instructor_user']['id'],
                "data_inicio": today.isoformat(),
                "data_fim": end_date.isoformat(),
                "horario_inicio": "08:00",
                "horario_fim": "12:00",
                "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
                "vagas_total": 25,
                "ciclo": "01/2025"
            }
            
            success, response, status = self.make_request('POST', 'classes', new_class, token=self.admin_token, expected_status=200)
            if success and 'id' in response:
                self.test_data['test_class_id'] = response['id']
                return self.log_test("Create Class", True, f"Created class with ID: {response['id']}")
            else:
                return self.log_test("Create Class", False, f"Status: {status}, Response: {response}")
        else:
            return self.log_test("Create Class", False, "Missing required data (units/courses)")

    def test_attendance_endpoints(self):
        """Test attendance CRUD operations"""
        print("\n📋 Testing Attendance Endpoints...")
        
        if not self.test_data.get('classes'):
            return self.log_test("Attendance Test", False, "No classes available for testing")

        # Get a class with students
        test_class = self.test_data['classes'][0]
        class_id = test_class['id']
        
        # Get students for the class
        success, students, status = self.make_request('GET', f'classes/{class_id}/students', token=self.instructor_token)
        if not success or not students:
            return self.log_test("Get Students for Attendance", False, f"Status: {status}")

        # Create attendance record
        today = date.today()
        now = datetime.now().strftime("%H:%M")
        
        # Create presencas dict with first 3 students present, rest absent
        presencas = {}
        for i, student in enumerate(students[:5]):  # Test with first 5 students
            presencas[student['id']] = {
                "presente": i < 3,  # First 3 present, rest absent
                "justificativa": "Teste automatizado" if i >= 3 else "",
                "atestado_id": ""
            }

        attendance_data = {
            "turma_id": class_id,
            "data": today.isoformat(),
            "horario": now,
            "observacoes_aula": "Aula de teste automatizado",
            "presencas": presencas
        }
        
        success, response, status = self.make_request('POST', 'attendance', attendance_data, token=self.instructor_token, expected_status=200)
        if success and 'id' in response:
            self.test_data['test_attendance_id'] = response['id']
            details = f"Created attendance with {response.get('total_presentes', 0)} present, {response.get('total_faltas', 0)} absent"
            return self.log_test("Create Attendance", True, details)
        else:
            return self.log_test("Create Attendance", False, f"Status: {status}, Response: {response}")

    def test_users_endpoints(self):
        """Test users management endpoints"""
        print("\n👥 Testing Users Endpoints...")
        
        # Get users (admin only)
        success, response, status = self.make_request('GET', 'users', token=self.admin_token)
        if success and isinstance(response, list):
            self.log_test("Get Users", True, f"Found {len(response)} users")
        else:
            self.log_test("Get Users", False, f"Status: {status}")

        # Test instructor access (should be forbidden)
        success, response, status = self.make_request('GET', 'users', token=self.instructor_token, expected_status=403)
        return self.log_test("Users Access Control", success, "Instructor correctly denied access")

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Auth Endpoints...")
        
        # Test /auth/me endpoint
        success, response, status = self.make_request('GET', 'auth/me', token=self.admin_token)
        if success and 'nome' in response:
            self.log_test("Get Current User", True, f"User: {response['nome']}")
        else:
            self.log_test("Get Current User", False, f"Status: {status}")

        # Test invalid token
        success, response, status = self.make_request('GET', 'auth/me', token="invalid_token", expected_status=401)
        return self.log_test("Invalid Token Handling", success, "Correctly rejected invalid token")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting IOS Sistema Backend API Tests")
        print("=" * 50)

        # Initialize system first
        if not self.test_system_initialization():
            print("❌ System initialization failed, continuing with tests...")

        # Authentication tests
        if not self.test_admin_login():
            print("❌ Admin login failed, cannot continue with admin tests")
            return False

        if not self.test_instructor_login():
            print("❌ Instructor login failed, cannot continue with instructor tests")

        # Core functionality tests
        self.test_dashboard_stats()
        self.test_auth_endpoints()
        self.test_units_endpoints()
        self.test_courses_endpoints()
        self.test_students_endpoints()
        self.test_classes_endpoints()
        self.test_attendance_endpoints()
        self.test_users_endpoints()

        # Print final results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend is working correctly.")
            return True
        else:
            failed = self.tests_run - self.tests_passed
            print(f"⚠️  {failed} tests failed. Check the issues above.")
            return False

def main():
    """Main test execution"""
    tester = IOSAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())