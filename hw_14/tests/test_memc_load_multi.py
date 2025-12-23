import pytest
from unittest.mock import patch, MagicMock
import sys

# Mock appsinstalled_pb2 before importing memc_load_multi
mock_appsinstalled_pb2 = MagicMock()
mock_user_apps = MagicMock()
mock_user_apps.SerializeToString.return_value = b"serialized_data"
mock_appsinstalled_pb2.UserApps.return_value = mock_user_apps
sys.modules['appsinstalled_pb2'] = mock_appsinstalled_pb2

# Mock memcache before importing memc_load_multi
mock_memcache = MagicMock()
sys.modules['memcache'] = mock_memcache

from memc_load_multi import process_file, main, prototest, AppsInstalled


@patch('memc_load_multi.dot_rename')
@patch('memc_load_multi.insert_appsinstalled')
@patch('memc_load_multi.process_line')
@patch('memc_load_multi.memcache.Client')
@patch('memc_load_multi.gzip.open')
def test_process_file(mock_gzip_open, mock_memc_client, mock_process_line, mock_insert, mock_dot_rename):
    """Test that process_file correctly processes lines and calls insert_appsinstalled."""
    # Mock gzip.open context manager
    mock_file = MagicMock()
    mock_file.readlines.return_value = [
        "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23",
        "gaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    ]
    mock_gzip_open.return_value.__enter__.return_value = mock_file
    mock_gzip_open.return_value.__exit__.return_value = False

    # Mock memcache client
    mock_client_instance = MagicMock()
    mock_memc_client.return_value = mock_client_instance

    # Mock process_line to return AppsInstalled objects
    mock_process_line.side_effect = [
        AppsInstalled("idfa", "1rfw452y52g2gq4g", 55.55, 42.42, [1423, 43, 567, 3, 7, 23]),
        AppsInstalled("gaid", "7rfw452y52g2gq4g", 55.55, 42.42, [7423, 424])
    ]

    # Mock insert_appsinstalled to return True (success)
    mock_insert.return_value = True

    device_memc = {
        'idfa': '127.0.0.1:33013',
        'gaid': '127.0.0.1:33014',
        'adid': '127.0.0.1:33015',
        'dvid': '127.0.0.1:33016'
    }

    # Call process_file
    process_file('test_file.gz', device_memc, False)

    # Assertions
    mock_gzip_open.assert_called_once_with('test_file.gz', 'rt')
    assert mock_process_line.call_count == 2
    assert mock_insert.call_count >= 1  # Should be called for each device type with data
    mock_dot_rename.assert_called_once_with('test_file.gz')


@patch('memc_load_multi.dot_rename')
@patch('memc_load_multi.insert_appsinstalled')
@patch('memc_load_multi.process_line')
@patch('memc_load_multi.memcache.Client')
@patch('memc_load_multi.gzip.open')
def test_process_file_with_errors(mock_gzip_open, mock_memc_client, mock_process_line, mock_insert, mock_dot_rename):
    """Test that process_file handles errors correctly."""
    mock_file = MagicMock()
    mock_file.readlines.return_value = [
        "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43"
    ]
    mock_gzip_open.return_value.__enter__.return_value = mock_file
    mock_gzip_open.return_value.__exit__.return_value = False

    mock_client_instance = MagicMock()
    mock_memc_client.return_value = mock_client_instance

    # process_line returns None (error)
    mock_process_line.return_value = None

    device_memc = {
        'idfa': '127.0.0.1:33013',
        'gaid': '127.0.0.1:33014',
        'adid': '127.0.0.1:33015',
        'dvid': '127.0.0.1:33016'
    }

    process_file('test_file.gz', device_memc, False)

    # File should still be renamed even if no records processed
    mock_dot_rename.assert_called_once_with('test_file.gz')


@patch('memc_load_multi.Thread')
@patch('memc_load_multi.glob.iglob')
def test_main(mock_iglob, mock_Thread):
    """Test that main creates threads for each file."""
    # Mock glob.iglob to return a list of filenames
    mock_iglob.return_value = ['file1.gz', 'file2.gz']

    # Mock Thread class
    mock_thread = MagicMock()
    mock_Thread.return_value = mock_thread

    # Create mock options
    options = MagicMock()
    options.idfa = '127.0.0.1:33013'
    options.gaid = '127.0.0.1:33014'
    options.adid = '127.0.0.1:33015'
    options.dvid = '127.0.0.1:33016'
    options.dry = False
    options.pattern = '/data/appsinstalled/*.tsv.gz'

    # Call main function
    main(options)

    # Assertions - Thread should be called twice (once for each file)
    assert mock_Thread.call_count == 2
    assert mock_thread.start.call_count == 2
    assert mock_thread.join.call_count == 2

    # Check that iglob was called with the correct pattern
    mock_iglob.assert_called_once_with('/data/appsinstalled/*.tsv.gz')


@patch('memc_load_multi.Thread')
@patch('memc_load_multi.glob.iglob')
def test_main_no_files(mock_iglob, mock_Thread):
    """Test that main handles empty file list correctly."""
    mock_iglob.return_value = []

    options = MagicMock()
    options.idfa = '127.0.0.1:33013'
    options.gaid = '127.0.0.1:33014'
    options.adid = '127.0.0.1:33015'
    options.dvid = '127.0.0.1:33016'
    options.dry = False
    options.pattern = '/data/appsinstalled/*.tsv.gz'

    main(options)

    # No threads should be created if no files
    mock_Thread.assert_not_called()


@patch('memc_load_multi.appsinstalled_pb2.UserApps')
def test_prototest(mock_UserApps):
    """Test that prototest function runs without errors."""
    # Setup mock UserApps
    mock_ua = MagicMock()
    mock_ua.SerializeToString.return_value = b"test_data"
    mock_UserApps.return_value = mock_ua

    # Call the prototest function - should not raise any exceptions
    prototest()

    # Verify UserApps was called
    assert mock_UserApps.call_count >= 1


def test_apps_installed_namedtuple():
    """Test that AppsInstalled namedtuple works correctly."""
    ai = AppsInstalled("idfa", "device123", 55.55, 42.42, [1, 2, 3])

    assert ai.dev_type == "idfa"
    assert ai.dev_id == "device123"
    assert ai.lat == 55.55
    assert ai.lon == 42.42
    assert ai.apps == [1, 2, 3]


if __name__ == '__main__':
    pytest.main()
