from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase


class HealthCheckTests(SimpleTestCase):
    @patch('core.views.connection.ensure_connection')
    def test_health_check_returns_ok_when_database_is_available(self, ensure_connection):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        ensure_connection.assert_called_once_with()

    @patch('core.views.connection.ensure_connection', side_effect=OperationalError)
    def test_health_check_returns_503_when_database_is_unavailable(self, ensure_connection):
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unhealthy'})
        ensure_connection.assert_called_once_with()
