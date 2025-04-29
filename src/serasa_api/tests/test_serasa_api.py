"""Test Neuron Lab API."""

import unittest
import configparser
import os
from serasa_api.data import SerasaAPI

config = configparser.ConfigParser()
dir_path = os.path.dirname(os.path.realpath(__file__))
config.read("{}/test_parameters.ini".format(dir_path))

SERASA_API_URL = config["DEFAULT"]["SERASA_API_URL"].strip()
SERASA_API_USERNAME = config["DEFAULT"]["SERASA_API_USERNAME"].strip()
SERASA_API_PASSWORD = config["DEFAULT"]["SERASA_API_PASSWORD"].strip()
CPF_TEST_INPUT = config["DEFAULT"]["CPF_TEST_INPUT"].strip()


class TestSerasaAPI(unittest.TestCase):
    """Test Neuron Lab api."""

    def test__fetch_advanced_report_pf(self):
        serasa_api = SerasaAPI(
            url=SERASA_API_URL,
            username=SERASA_API_USERNAME,
            password=SERASA_API_PASSWORD,
        )

        reports = serasa_api.person_advanced_report(CPF_TEST_INPUT)

        self.assertEqual(reports["reportName"], "RELATORIO_AVANCADO_PF")
        self.assertEqual(
            reports["registration"]["documentNumber"], CPF_TEST_INPUT
        )
