from app.services.scan_service import apply_dhcp_range_status, map_scan_result


def test_map_scan_result_conflict_and_unknown():
    existing = {'192.168.1.10'}
    scanned = ['192.168.1.10', '192.168.1.11']

    result = map_scan_result(existing, scanned)

    assert result[0]['status'] == 'CONFLICT'
    assert result[1]['status'] == 'UNKNOWN'


def test_apply_dhcp_range_status_marks_dhcp_inside_range():
    rows = [
        {'address': '192.168.1.10', 'status': 'UNKNOWN', 'mac_address': None},
        {'address': '192.168.1.210', 'status': 'UNKNOWN', 'mac_address': None},
    ]

    result = apply_dhcp_range_status(rows, '192.168.1.2', '192.168.1.200')

    assert result[0]['status'] == 'DHCP'
    assert result[1]['status'] == 'UNKNOWN'
