import os

from io import open

from unittest import TestCase

from ...bencode import bdecode

from ..transmission import TransmissionClient as RealTransmissionClient

current_path = os.path.dirname(__file__)


class TransmissionClient(RealTransmissionClient):
    def __init__(self, *args, **kwargs):
        super(TransmissionClient, self).__init__(*args, **kwargs)
        self._torrents = {}
        self._torrent_id = 1
    
    def call(self, method, **kwargs):
        if method == 'session-get':
            return {'version': 'version: 2.82 (14160)',
                    'config-dir': '/home/autotorrent/.config/transmission-daemon',
                    'download-dir': '/home/autotorrent/Downloads',
                    'rpc-version': 15}
        elif method == 'torrent-add':
            self._torrent_id += 1
            self._torrents[self._torrent_id] = kwargs
            return {'torrent-added': {'id': self._torrent_id}}
        elif method == 'torrent-rename-path':
            self._torrents[kwargs['ids'][0]].update(kwargs)
            return {}
        elif method == 'torrent-start':
            self._torrents[kwargs['ids'][0]]['paused'] = False
            return {}
        else:
            raise Exception(method, kwargs)

class TestTransmissionClient(TestCase):
    def setUp(self):
        self.client = TransmissionClient('http://127.0.0.1:9091')
    
    def test_test_connection(self):
        self.assertEqual(self.client.test_connection(), "version: 2.82 (14160), config-dir: /home/autotorrent/.config/transmission-daemon, download-dir: /home/autotorrent/Downloads")
    
    def _add_torrent_with_links(self, letters):
        with open(os.path.join(current_path, 'test.torrent'), 'rb') as f:
            torrent = bdecode(f.read())
    
        files = []
        for letter in ['a', 'b', 'c']:
            filename = 'file_%s.txt' % letter
            files.append({
                'completed': (letter in letters),
                'length': 11,
                'path': ['tmp', filename],
            })
        
        return self.client.add_torrent(torrent, '/tmp/', files)
    
    
    def test_add_torrent_complete(self):
        self.assertTrue(self._add_torrent_with_links(['a', 'b', 'c']))
        self.assertIn(2, self.client._torrents)
        self.assertEqual(self.client._torrents[2]['paused'], False)
    