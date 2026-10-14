
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By


class ResumeAnalyzerTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)

    def test_resume_upload_page(self):
        self.driver.get("http://127.0.0.1:5001/")

        self.assertEqual(
            self.driver.current_url,
            "http://127.0.0.1:5001/"
        )

        upload_fields = self.driver.find_elements(
            By.CSS_SELECTOR, "input[type='file'][name='resume']"
        )

        self.assertGreater(
            len(upload_fields), 0,
            "Resume upload field was not found"
        )

        print("PASS: Resume Analyzer page opened")
        print("PASS: Resume upload field was found")

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)


