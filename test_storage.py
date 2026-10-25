import tempfile
import unittest
from pathlib import Path


class StorageTests(unittest.TestCase):
    def test_configuration_persists_and_isolated_by_server(self):
        try:
            from storage import ConfigStore
        except ImportError:
            self.fail('ConfigStore ainda não implementado')
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path = Path(folder) / 'config.sqlite3'
            store = ConfigStore(path)
            self.assertFalse(store.get(1)['configured'])
            store.update(1, provider='groq', model='example', agent='Ajude.', tone='formal', configured=True)
            reopened = ConfigStore(path)
            self.assertEqual(reopened.get(1)['model'], 'example')
            self.assertEqual(reopened.get(1)['tone'], 'formal')
            self.assertFalse(reopened.get(2)['configured'])
            with self.assertRaises(ValueError):
                reopened.update(1, api_key='never-store-secrets')


if __name__ == '__main__':
    unittest.main()
