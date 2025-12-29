import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import datetime
from io import StringIO

# Append parent directory to path to import check_speed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import check_speed

class TestCheckSpeed(unittest.TestCase):

    def setUp(self):
        # Create a dummy log file
        self.test_log_file = 'test_speed_log.txt'

    def tearDown(self):
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_log_results(self):
        check_speed.log_results(100.0, 50.0, 10.0, '1234', 'Test Server', self.test_log_file)
        self.assertTrue(os.path.exists(self.test_log_file))
        with open(self.test_log_file, 'r') as f:
            content = f.read()
            self.assertIn('100.0', content)
            self.assertIn('50.0', content)
            self.assertIn('10.0', content)
            self.assertIn('1234', content)
            self.assertIn('Test Server', content)

    def test_calculate_averages_no_file(self):
        # Ensure no file exists
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

        dl, ul, ping = check_speed.calculate_averages(self.test_log_file)
        self.assertIsNone(dl)
        self.assertIsNone(ul)
        self.assertIsNone(ping)

    def test_calculate_averages_with_data(self):
        with open(self.test_log_file, 'w') as f:
            f.write("2025-01-01T12:00:00,100.0,50.0,10.0,1,S1\n")
            f.write("2025-01-01T13:00:00,200.0,100.0,20.0,2,S2\n")

        dl, ul, ping = check_speed.calculate_averages(self.test_log_file)
        self.assertEqual(dl, 150.0)
        self.assertEqual(ul, 75.0)
        self.assertEqual(ping, 15.0)

    def test_calculate_averages_corrupt_data(self):
         with open(self.test_log_file, 'w') as f:
            f.write("2025-01-01T12:00:00,100.0,50.0,10.0,1,S1\n")
            f.write("garbage line\n")
            f.write("2025-01-01T13:00:00,200.0,100.0,20.0,2,S2\n")

         dl, ul, ping = check_speed.calculate_averages(self.test_log_file)
         self.assertEqual(dl, 150.0)
         self.assertEqual(ul, 75.0)
         self.assertEqual(ping, 15.0)

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_get_official_speedtest_command(self, mock_run, mock_which):
        # Mock successful finding of speedtest
        mock_which.return_value = '/usr/bin/speedtest'
        mock_run.return_value.stdout = "Ookla Speedtest 1.2.3"

        cmd = check_speed.get_official_speedtest_command()
        # It returns 'speedtest' because it iterates over candidates and the first one 'speedtest' matches mock_which(cmd)
        self.assertEqual(cmd, 'speedtest')

    @patch('shutil.which')
    def test_get_official_speedtest_command_not_found(self, mock_which):
        mock_which.return_value = None
        cmd = check_speed.get_official_speedtest_command()
        self.assertIsNone(cmd)

    @patch('subprocess.run')
    def test_get_server_id_by_name(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            'servers': [
                {'name': 'Test Server', 'location': 'Test Location', 'host': 'test.host', 'id': '1234'},
                {'name': 'Other Server', 'location': 'Other Location', 'host': 'other.host', 'id': '5678'}
            ]
        })

        server_id = check_speed.get_server_id_by_name('speedtest', 'Test')
        self.assertEqual(server_id, '1234')

        server_id = check_speed.get_server_id_by_name('speedtest', 'Other')
        self.assertEqual(server_id, '5678')

        server_id = check_speed.get_server_id_by_name('speedtest', 'Nonexistent')
        self.assertIsNone(server_id)

    @patch('subprocess.run')
    def test_get_server_id_by_name_error(self, mock_run):
        mock_run.return_value.returncode = 1
        server_id = check_speed.get_server_id_by_name('speedtest', 'Test')
        self.assertIsNone(server_id)

if __name__ == '__main__':
    unittest.main()
