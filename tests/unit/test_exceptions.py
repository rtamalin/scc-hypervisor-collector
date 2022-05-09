import pytest

from scc_hypervisor_collector.api import exceptions

class TestExceptions:
  
    def test_empty_exception_message(self):
        e = exceptions.CollectorException()
        assert e.message is None