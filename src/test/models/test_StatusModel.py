import unittest

from ...models import StatusModel


class Test(unittest.TestCase):

    def test_get_all(self):
        res = StatusModel.get_all()
        self.assertEqual(len(res), 6)

        for status in res:
            self.assertIsInstance(status, StatusModel.Status)
            self.assertIsInstance(status.label, str)
            self.assertIsInstance(status.value, str)
