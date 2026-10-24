import json
import io
import unittest
from app import app
from database.seed_data import seed

class SafeJobsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed()
        cls.client = app.test_client()
        cls.client.testing = True

    def test_health_check(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_home_page(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SafeJobs", res.data)

    def test_text_analysis_scam(self):
        # Amazon remote data entry scam sample
        payload = {
            "text_content": "Congratulations! You have been selected for Amazon remote data entry. Pay $180 laptop deposit via CashApp to finalize. Contact on Telegram @Amazon_Recruiter.",
            "sender_email": "recruiting-amazon@gmail.com",
            "claimed_company": "Amazon"
        }
        res = self.client.post('/api/analyze/text', 
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analysis = data["data"]
        self.assertGreaterEqual(analysis["scam_score"], 70)
        self.assertTrue(analysis["fee_demanded"])
        self.assertIn("domain_analysis", analysis)
        self.assertTrue(analysis["domain_analysis"]["is_free_provider"])

    def test_text_analysis_legit(self):
        payload = {
            "text_content": "Thank you for speaking with us regarding the Software Engineer position. Please review the official posting on https://careers.google.com/jobs/results/GOOG-SWE-55102 and schedule your technical round on Google Meet. Google never charges any recruitment fee.",
            "sender_email": "recruiting@google.com",
            "claimed_company": "Google"
        }
        res = self.client.post('/api/analyze/text',
                               data=json.dumps(payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        analysis = data["data"]
        self.assertLess(analysis["scam_score"], 45)

    def test_career_verification_active(self):
        # Test active job opening for TCS Systems Engineer
        res = self.client.get('/api/careers/verify?company=TCS&role=Systems%20Engineer')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertTrue(data["verified"])
        self.assertEqual(data["status"], "OFFICIALLY_VERIFIED_ON_CAREERS_PAGE")
        self.assertIsNotNone(data["matched_job"])
        self.assertEqual(data["matched_job"]["job_id"], "TCS-ENG-2026-902")

    def test_career_verification_fake_role(self):
        # Test fake role that Amazon does not have
        res = self.client.get('/api/careers/verify?company=Amazon&role=Remote%20Data%20Entry%20Clerk')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertFalse(data["verified"])
        self.assertEqual(data["status"], "NO_OFFICIAL_POSTING_FOUND")

    def test_company_report_check(self):
        # Test checking reported company
        res = self.client.get('/api/reports/check?query=careers-amazon-global@gmail.com')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertTrue(data["reported"])
        self.assertGreater(data["count"], 0)

    def test_submit_new_report(self):
        report_data = {
            "company_name": "Test Phish Corp",
            "scam_type": "Advance Fee / Equipment Scam",
            "sender_email": "hr@test-fake-phish.xyz",
            "sender_phone": "+91 99999 88888",
            "job_title": "Telegram Video Rater",
            "loss_amount": 75,
            "description": "Asked for $75 VIP registration fee to start liking videos."
        }
        res = self.client.post('/api/reports/submit', data=report_data)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

        # Check it is now in the database
        check_res = self.client.get('/api/reports/check?query=test-fake-phish.xyz')
        self.assertTrue(check_res.get_json()["data"]["reported"])

    def test_image_analysis_endpoint(self):
        # Test uploading an image file
        with open("static/images/sample-telegram-scam.jpg", "rb") as f:
            img_bytes = f.read()

        data = {
            'image_file': (io.BytesIO(img_bytes), 'test_scan.jpg'),
            'notes': 'Received on Telegram'
        }
        res = self.client.post('/api/analyze/image', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data["success"])
        self.assertIn("scam_score", res_data["data"])

if __name__ == '__main__':
    unittest.main()
