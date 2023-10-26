import unittest
import json
from webapp import create_app, db
from webapp.auth.models import User, Role
from webapp.admin import admin
from webapp.api import rest_api
import re

class TestURLs(unittest.TestCase):
    def setUp(self):
        admin._views = []
        rest_api.resources = []

        app = create_app('config.TestConfig')
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        db.app = app
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_root_redirect(self):
        """Tests if the root URl gives 302 """
        result = self.client.get('/')
        assert result.status_code == 302
        assert "/blog/" in result.headers['Location']

    def test_blog_home(self):
        """Tests if the blog home page returns successfully"""
        result = self.client.get('/blog/')
        self.assertEqual(result.status_code, 200)
    
    def _insert_user(self, username, password, role_name):
        test_role = Role(role_name)
        db.session.add(test_role)
        db.session.commit()

        test_user = User(username)
        test_user.set_password(password)
        db.session.add(test_user)
        db.session.commit()

    def test_login(self):
        """Tests if the login form works correctly"""
        self._insert_user("test", "test", "default")
        result = self.client.post('/auth/login', data=dict(
            username='test',
            password="test"
        ), follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'You have been logged in.', result.data)

    def test_failed_login(self):
        """Tests login failure"""
        self._insert_user("test", "test", "default")
        result = self.client.post('/auth/login', data=dict(
            username="test",
            password="incorrect password"
        ), follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Invalid username or password", result.data)
        result = self.client.get('/blog/new_post')
        self.assertEqual(result.status_code, 302)
    
    def test_unauthorized_access_to_admin(self):
        """Tests unauthorized admin access"""
        self._insert_user('test','test','default')
        result = self.client.post('/auth/login', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)
        result = self.client.get('/admin/customview/')
        self.assertEqual(result.status_code, 403)

    def test_unauthorized_access_to_post(self):
        """Tests unauthorized post creation"""
        self._insert_user('test', 'test', 'default')
        result = self.client.post('/auth/login', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)
        result = self.client.get('/blog/new_post')
        self.assertEqual(result.status_code, 403)
    
    def test_logout(self):
        """Tests if the logout works correctly"""
        self._insert_user('test', 'test', 'default')
        result = self.client.post('/auth/logout', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'You have been logged out.', result.data)

    def test_api_jwt_login(self):
        """Test API JWT Login"""
        self._insert_user('test', 'test', 'default')
        headers = {'content-type':'application/json'}
        result = self.client.post('/auth/api', headers=headers,data='{"username":"test","password":"test"}')
        self.assertEqual(result.status_code, 200)

    def test_api_jwt_failed_login(self):
        """Test API JWT Failed Login"""
        self._insert_user('test', 'test', 'default')
        headers = {'content-type':'application/json'}
        result = self.client.post('/auth/api', headers=headers,data='{"username":"test","password":"wrongpassword"}')
        self.assertEqual(result.status_code, 401)

    def test_api_new_post(self):
        """Test API new post"""
        self._insert_user('test', 'test', 'default')
        headers = {'content-type':'application/json'}
        result = self.client.post('/auth/api', headers=headers,data='{"username":"test","password":"test"}')
        access_token = json.loads(result.data)['access_token']
        headers['Authorization'] = "Bearer %s" % access_token
        result = self.client.post('api/post', headers=headers, data='{"title":"Text Title","text":"Changed"}')
        self.assertEqual(result.status_code, 201)

if __name__ == '__main__':
    unittest.main()