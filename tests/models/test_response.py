from unittest import TestCase

from xrpl.models.response import Response, ResponseStatus


class TestResponse(TestCase):
    def test_is_successful_true(self):
        response = Response(status=ResponseStatus.SUCCESS, result={})
        self.assertTrue(response.is_successful())

    def test_is_successful_false(self):
        response = Response(status=ResponseStatus.ERROR, result={})
        self.assertFalse(response.is_successful())
