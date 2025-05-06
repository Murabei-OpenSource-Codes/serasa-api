"""Serasa Experian Python API."""
import requests
import os
import time
from typing import Dict, Any
from copy import copy
from urllib.parse import urljoin
from serasa_api.exceptions import (
    SerasaAPIQueryErrorException,
    SerasaAPILoginErrorException,
    SerasaAPIMalformedOutputException)

# Constants
API_HEADERS = {"Content-Type": "application/json"}
MAX_TIMEOUT = int(os.getenv("SERASA_API_MAX_TIMEOUT", 60))


# Serasa API communication class
class SerasaAPI:
    """Serasa API wrapper."""

    _username: str
    """Username that will be used to request login token."""
    _password: str
    """Password that will be used to request login token."""
    _url: str
    """URL that will be used to call Serasa end-points."""

    def __init__(self, username: str, password: str, url: str,
                 proxy: str = None):
        """_init_.

        Args:
            username (str):
                Basic Auth username.
            password (str):
                Basic Auth password.
            url (str):
                API URL.
            proxy (str):
                Proxy URL.
        """
        # Access properties.
        self._username = username
        self._password = password
        self._url = url

        # Token data, revalidated every request.
        self._token_data = None

        # Proxy setup.
        if proxy is None:
            proxy = os.getenv("SERASA_API_PROXY")
        self._proxy = proxy

        # Session and proxy: create a session object and set proxy.
        self._session = requests.Session()
        self._session.proxies = {"http": self._proxy, "https": self._proxy}

    def person_advanced_report(self, cpf: str) -> dict:
        """Fetch advanced report 'RELATORIO_AVANCADO_PF' in Serasa API.

        Args:
            cpf (str):
                Person CPF.

        Returns:
            dict:
                Person advanced report.
        """
        return self._person_information_report(
            cpf=cpf, report_name="RELATORIO_AVANCADO_PF")

    # Private methods:
    def _person_information_report(self, cpf: str,
                                    report_name: str) -> dict:
        """Queries person information reports in Serasa API.

        Args:
            cpf (str):
                Person CPF.
            report_name (str):
                Name of report to be fetch.

        Returns:
            dict:
                Person reports.

        Raises:
            SerasaAPIMalformedOutputException:
                Raise error if the data returned is not valid.
        """
        resource = "credit-services/person-information-report/v1/creditreport"

        headers_opt = {
            "X-Document-Id": cpf,
        }

        parameters = {"reportName": report_name}

        query_result = self._query(
            resource=resource, parameters=parameters,
            headers_opt=headers_opt)

        if "reports" not in query_result and len(query_result["reports"]) < 1:
            raise SerasaAPIMalformedOutputException(
                message="Output should have at least one report",
                payload=query_result,
            )

        # return the first report in the list
        return query_result["reports"][0]

    def _query(self, resource: str, parameters: dict, headers_opt: dict):
        """Query a resource in Serasa API.

        Args:
            resource (str):
                The resource to be reached in Serasa API.
            parameters (dict):
                URL query parameters.
            headers_opt (dict):
                Additional headers.

        Returns:
            requests.Response:
                Query response.
        """
        api_url = urljoin(base=self._url, url=resource)
        headers = self._signed_header()
        if headers_opt:
            headers.update(headers_opt)

        try:
            response = self._session.get(
                api_url, params=parameters, headers=headers,
                timeout=MAX_TIMEOUT)
            response.raise_for_status()
            query_result = response.json()

            return query_result
        except requests.exceptions.HTTPError as e:
            response_list = e.response.json()
            response_error = response_list[0]

            raise SerasaAPIQueryErrorException(
                message=response_error["message"], payload=response_error
            )

    def _signed_header(self):
        """Create a signed header to performs authorized API requests.

        Returns:
            dict:
                signed headers.
        """
        # Get the authorization token.
        self._login()

        # Mount Authorization field
        token_type = self._token_data["token_type"]
        token_value = self._token_data["access_token"]
        token = "{} {}".format(token_type, token_value)

        headers = copy(API_HEADERS)
        headers["Authorization"] = token

        return headers

    def _login(self):
        """Make a request to login endpoint to authenticate the API access."""
        resource = "security/iam/v1/client-identities/login"

        # Return if token is alive
        if self._token_alive():
            return

        # Setup access headers & authorization
        headers = copy(API_HEADERS)

        try:
            api_url = urljoin(base=self._url, url=resource)
            response = self._session.post(
                api_url, headers=headers,
                timeout=MAX_TIMEOUT, auth=(self._username, self._password))

            # Get token data
            response.raise_for_status()
            response_json = response.json()
            treated_response = {
                "access_token": response_json["accessToken"],
                "token_type": response_json["tokenType"],
                "expires_in": response_json["expiresIn"],
                "scope": response_json["scope"],
            }

            self._token_data = treated_response
        except requests.exceptions.HTTPError as e:
            response_list = e.response.json()
            response_error = response_list[0]

            raise SerasaAPILoginErrorException(
                message=response_error["message"],
                payload=response_error)

    def _token_alive(self):
        """Check if token exists and is valid.

        Returns:
            boolean:
                true if token is valid, otherwise false.
        """
        # Invalid if no token is provided.
        if self._token_data is None:
            return False

        # Check if existent token stills valid.
        expires_in = self._token_data["expires_in"]
        try:
            timestamp = int(expires_in) - 300
            now = int(time.time())
            return timestamp <= now
        except ValueError:
            return False
