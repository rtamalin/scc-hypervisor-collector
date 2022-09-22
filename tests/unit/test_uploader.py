from collections import namedtuple
import mock
import pytest
from requests.exceptions import RequestException

from scc_hypervisor_collector.api import (
    SccCredsConfig,
    SCCUploader
)

FakeResponse = namedtuple('FakeResponse', 'status_code')
required_uploader_headers = [
    'X-Gatherer-Version',
    'X-Scc-Hypervisor-Collector-Version',
    'Content-Type',
]

class TestUploader:

    def test_uploader_init(self):
        scc_url1 = 'https://scc1.example.com'
        scc_url2 = 'https://scc2.example.com'
        scc_token = 'dummy_token'

        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url1))
        assert scc_creds.url == scc_url1

        with mock.patch('requests.auth.HTTPBasicAuth',
                        return_value=scc_token) as http_basic_auth:
            uploader = SCCUploader(scc_creds,
                                   scc_base_url=scc_url2)
            http_basic_auth.assert_called_with(scc_creds.username,
                                               scc_creds.password)
            assert uploader.scc_base_url != scc_url1
            assert uploader.scc_base_url == scc_url2
            assert uploader.auth == scc_token
            assert all(h in uploader.headers
                       for h in required_uploader_headers)


    def test_uploader_check_creds(self):
        scc_url = 'https://scc.example.com'
        scc_token = 'dummy_token'
        scc_test_path = '/test'
        scc_payload = 'compressed_data'
        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url))
        uploader = SCCUploader(scc_creds)

        with mock.patch('requests.get', return_value=FakeResponse(200)
                       ) as requests_get:
            response = uploader.check_creds(path=scc_test_path)
            requests_get.assert_called_with(
                scc_url + scc_test_path,
                auth=uploader.auth,
                headers=uploader.headers,
                allow_redirects=False
            )


    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_upload_hypervisor_details_to_scc_success(self, collected_results):
        scc_url = 'https://scc.example.com'
        scc_test_path = '/test'
        scc_payload = 'compressed_data'

        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url))

        uploader = SCCUploader(scc_creds)

        with mock.patch('requests.put', return_value=FakeResponse(200)
                       ) as requests_put:
            for results in collected_results.results:
                with mock.patch('gzip.compress', return_value=scc_payload):
                    uploader.upload(details=results['details'],
                                    backend=results['backend'],
                                    path=scc_test_path)
                    requests_put.assert_called_with(
                        scc_url + scc_test_path,
                        auth=uploader.auth,
                        headers=uploader.headers,
                        data=scc_payload,
                        allow_redirects=False
                    )


    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_upload_hypervisor_details_to_scc_failed(self, collected_results):
        scc_url = 'https://scc.example.com'
        scc_test_path = '/test'
        scc_payload = 'compressed_data'

        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url))

        uploader = SCCUploader(scc_creds)

        with mock.patch('requests.put', return_value=FakeResponse(500)
                       ) as requests_put:
            for results in collected_results.results:
                with mock.patch('gzip.compress', return_value=scc_payload):
                    uploader.upload(details=results['details'],
                                    backend=results['backend'],
                                    path=scc_test_path)
                    requests_put.assert_called_with(
                        scc_url + scc_test_path,
                        auth=uploader.auth,
                        headers=uploader.headers,
                        data=scc_payload,
                        allow_redirects=False
                    )


    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_upload_hypervisor_details_to_scc_retry(self, collected_results):
        scc_url = 'https://scc.example.com'
        scc_test_path = '/test'
        scc_payload = 'compressed_data'

        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url))

        uploader = SCCUploader(scc_creds)

        with mock.patch('requests.put', return_value=FakeResponse(429)
                       ) as requests_put:
            for results in collected_results.results:
                with mock.patch('gzip.compress', return_value=scc_payload):
                    uploader.upload(details=results['details'],
                                    backend=results['backend'],
                                    path=scc_test_path)
                    requests_put.assert_called_with(
                        scc_url + scc_test_path,
                        auth=uploader.auth,
                        headers=uploader.headers,
                        data=scc_payload,
                        allow_redirects=False
                    )


    @pytest.mark.config('tests/unit/data/collected/libvirt/collector.results')
    def test_upload_hypervisor_details_put_exception(self, collected_results):
        scc_url = 'https://scc.example.com'
        scc_test_path = '/test'
        scc_payload = 'compressed_data'

        scc_creds = SccCredsConfig(dict(password='someuser',
                                        username='somepass',
                                        url=scc_url))

        uploader = SCCUploader(scc_creds)

        with mock.patch('requests.put', return_value=FakeResponse(200)
                       ) as requests_put:
            for results in collected_results.results:
                with mock.patch('gzip.compress', return_value=scc_payload):
                    requests_put.side_effect = RequestException("Failed")
                    uploader.upload(details=results['details'],
                                    backend=results['backend'],
                                    path=scc_test_path)
