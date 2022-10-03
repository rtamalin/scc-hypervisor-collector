"""
SCC Hypervisor Collector SCCUploader

The SCCUploader is responsible for uploading the hypervisor details
collected from the specified backends to the SCC using the provided
credentials.
"""
import json
import logging
import gzip
import sys
import time
from typing import (Dict, Optional)
from importlib_metadata import version as get_package_version
import requests
from requests.exceptions import RequestException

from .configuration import SccCredsConfig


class SCCUploader:
    """SCC Uploader for scc-hypervisor-collector."""

    def __init__(self, scc_creds: SccCredsConfig,
                 scc_base_url: Optional[str] = None):
        """Initialiser for SCCUploader"""
        self._log = logging.getLogger(__name__)

        # handle default parameters
        if scc_base_url is None:
            scc_base_url = scc_creds.url

        # save the parameters
        self._scc_creds = scc_creds
        self.auth = requests.auth.HTTPBasicAuth(self._scc_creds.username,
                                                self._scc_creds.password)

        self.headers = {
            'X-Gatherer-Version':
                get_package_version('virtual-host-gatherer'),
            'X-Scc-Hypervisor-Collector-Version':
                get_package_version('scc-hypervisor-collector'),
            'Content-Type': 'application/json'
        }
        self.scc_base_url = scc_base_url

    def upload(self, details: Dict, backend: str,
               retry: bool = False,
               path: str =
               '/connect/organizations/virtualization_hosts') -> None:
        """ Upload the collected details to SCC"""
        try:
            response = self.scc_put(details=details, path=path)
            self.check_response_status(response, backend)
            if response.status_code == 429:
                self._log.error("Too many requests have been sent to SCC")
                retry_delay_secs = int(response.headers.get('Retry-After',
                                                            300))
                if retry:
                    self._log.info("Waiting to upload to SCC for %s seconds "
                                   "before sending the request "
                                   "again", retry_delay_secs)
                    response = self.scc_put(details=details,
                                            path=path,
                                            delay=retry_delay_secs)
                    self.check_response_status(response, backend)
                else:
                    self._log.error("Program will exit as it hit the rate "
                                    "limit sending requests to SCC")
                    sys.exit(0)
        except RequestException:
            error_msg = "upload to scc failed "
            self._log.error(error_msg)

    def scc_put(self, details: Dict, path: str,
                delay: int = 0) -> requests.Response:
        """
        Calls the virtualization_hosts SCC API to upload the hypervisor details
        """
        headers = self.headers
        headers.update({'Content-Encoding': 'gzip'})
        zipped_payload = gzip.compress(json.dumps(details).encode('utf-8'))

        if delay != 0:
            time.sleep(delay)

        response = requests.put(self.scc_base_url + path,
                                auth=self.auth,
                                headers=headers,
                                data=zipped_payload,
                                allow_redirects=False)

        return response

    def check_creds(self,
                    path: str =
                    '/connect/organizations/repositories') -> bool:
        """
        Return True if the GET call to the path is successful
        """
        response = requests.get(self.scc_base_url + path,
                                auth=self.auth,
                                headers=self.headers,
                                allow_redirects=False)
        return response.status_code == 200

    def check_response_status(self, response: requests.Response,
                              backend: str) -> None:
        """
        Check the response status and log appropriately
        """
        if response.status_code == 200:
            self._log.info("Successfully Uploaded details to SCC for %s",
                           backend)
        else:
            self._log.error("Failed to Upload details to SCC for %s",
                            backend)
