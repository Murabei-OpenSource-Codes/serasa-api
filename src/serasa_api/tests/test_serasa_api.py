"""Test Neuron Lab API."""
import os
import unittest
from serasa_api.data import SerasaAPI

SERASA_API_URL = os.getenv("SERASA_API_URL")
SERASA_API_USERNAME = os.getenv("SERASA_API_USERNAME")
SERASA_API_PASSWORD = os.getenv("SERASA_API_PASSWORD")
CPF_TEST_INPUT = os.getenv("CPF_TEST_INPUT")


class TestSerasaAPI(unittest.TestCase):
    """Test Neuron Lab api."""

    def test__fetch_advanced_report_pf(self):
        """Test fetch advanced report pf."""
        serasa_api = SerasaAPI(
            url=SERASA_API_URL, username=SERASA_API_USERNAME,
            password=SERASA_API_PASSWORD)

        reports = serasa_api.person_advanced_report(CPF_TEST_INPUT)

        self.assertEqual(reports["reportName"], "RELATORIO_AVANCADO_PF")
        self.assertEqual(
            reports["registration"]["documentNumber"], CPF_TEST_INPUT
        )
