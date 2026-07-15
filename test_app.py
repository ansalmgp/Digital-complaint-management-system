import unittest
from app import app
from models.db import init_db, query_db

class TestComplaintSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Force db re-initialization before testing
        init_db(force=True)
        cls.client = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False

    def setUp(self):
        # Clean session/cookies before each test to ensure test isolation
        with self.client.session_transaction() as sess:
            sess.clear()

    def test_01_homepage_redirect(self):
        """Home page should redirect to login page for visitors."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.location)

    def test_02_student_login_success(self):
        """Student should be able to log in with correct credentials."""
        res = self.client.post('/login', data={
            'role': 'student',
            'email': 'amit@college.edu',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Student Dashboard', res.data)
        self.assertIn(b'Amit Sharma', res.data)

    def test_03_student_login_fail(self):
        """Student login should fail with wrong credentials."""
        res = self.client.post('/login', data={
            'role': 'student',
            'email': 'amit@college.edu',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Invalid email or password', res.data)

    def test_04_submit_complaint(self):
        """Student should be able to submit a complaint and trigger notification flow."""
        # Establish student session manually
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'student'
            sess['user_name'] = 'Amit Sharma'
            sess['user_email'] = 'amit@college.edu'
            
        res = self.client.post('/student/submit', data={
            'title': 'Test Cooler Breakdown',
            'category': 'Facilities',
            'description': 'Water leaking on second floor near CSE computer labs.'
        }, follow_redirects=True)
        
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Your complaint has been submitted successfully!', res.data)
        
        # Verify entry exists in Database
        complaint = query_db("SELECT * FROM Complaints WHERE Title = %s", ('Test Cooler Breakdown',), one=True)
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint['Status'], 'Pending')
        self.assertEqual(complaint['Category'], 'Facilities')
        
        # Verify notification was logged
        notif = query_db("SELECT * FROM Notifications WHERE StudentID = %s ORDER BY CreatedDate DESC LIMIT 1", (1,), one=True)
        self.assertIsNotNone(notif)
        self.assertIn('Test Cooler Breakdown', notif['Message'])

    def test_05_admin_login_success(self):
        """Administrator should be able to log in with pre-seeded credentials."""
        res = self.client.post('/login', data={
            'role': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Administrator Dashboard', res.data)

    def test_06_admin_update_status(self):
        """Administrator should be able to assign, comment, and change ticket status."""
        # Setup session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_type'] = 'admin'
            sess['user_name'] = 'admin'
            
        # Get latest filed complaint ID from DB (which is complaint 5 or 6)
        complaint = query_db("SELECT ComplaintID FROM Complaints ORDER BY CreatedDate DESC LIMIT 1", one=True)
        c_id = complaint['ComplaintID']
        
        # Post status update
        res = self.client.post(f'/admin/complaints/{c_id}', data={
            'status': 'Under Review',
            'assignee': 'Maintenance Team B',
            'remarks': 'Plumber has been dispatched.'
        }, follow_redirects=True)
        
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'status updated successfully to', res.data)
        
        # Verify status update in Complaints table
        updated = query_db("SELECT Status FROM Complaints WHERE ComplaintID = %s", (c_id,), one=True)
        self.assertEqual(updated['Status'], 'Under Review')
        
        # Verify History Log trail by ordering by HistoryID DESC
        history = query_db("SELECT * FROM ComplaintHistory WHERE ComplaintID = %s ORDER BY HistoryID DESC LIMIT 1", (c_id,), one=True)
        self.assertEqual(history['NewStatus'], 'Under Review')
        self.assertIn('Maintenance Team B', history['Remarks'])
        self.assertIn('Plumber has been dispatched', history['Remarks'])

if __name__ == '__main__':
    unittest.main()

