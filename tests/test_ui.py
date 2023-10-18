import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class TestURLs(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
    
    def tearDown(self):
        self.driver.close()

    def test_add_new_post(self):
        """Tests if the new post page saves a Post object to the
            database
            1.Log in the user
            2.Go to the new_post page
            3.Fill out the fields and submit the form
            4.Go to the blog home page and verify that the post is
            available.  
        """
        self.driver.get("http://localhost:4000/auth/login")

        username_field = self.driver.find_element(By.NAME, "username")
        username_field.send_keys("test")
        password_field = self.driver.find_element(By.NAME, "password")
        password_field.send_keys("test")
        login_button = self.driver.find_element(By.NAME, "submit")
        login_button.click()

        # fill out the PostForm
        self.driver.get("http://localhost:4000/blog/new_post")

        title_field = self.driver.find_element(By.NAME, "title")
        title_field.send_keys("Title Example")
        content_field = self.driver.find_element(By.NAME, "text")
        content_field.send_keys("Content Example")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary")
        submit_button.click()

        # verify the post was created
        self.driver.get('http://localhost:4000/blog')
        self.assertIn("Title Example", self.driver.page_source)
        self.assertIn("Content Example", self.driver.page_source)

if __name__ == "__main__":
    unittest.main()