import json

def read_mock_data(filename):
    f = open(filename)
    data = json.load(f)
    return data

def validate_mock_data(hypervisorcollector, backend_id):
    #based on the contents in test/unit/data/config/mock
    assert backend_id == hypervisorcollector.backend.id
    if backend_id == 'libvirt1':
        assert 'sle15-dev' in hypervisorcollector.hosts
        assert 'sle15-dev' in hypervisorcollector.details
        assert 'sle15-dev' in hypervisorcollector.results
    if backend_id == 'libvirt2':
        assert 'sle15-dev-2' in hypervisorcollector.hosts
        assert 'sle15-dev-2' in hypervisorcollector.details
        assert 'sle15-dev-2' in hypervisorcollector.results
    if backend_id == 'vcenter1':
        assert 'esx1.test.net' in hypervisorcollector.hosts
        assert 'esx1.test.net' in hypervisorcollector.details
        assert 'esx2.test.net' in hypervisorcollector.details
        assert 'esx1.test.net' in hypervisorcollector.results
