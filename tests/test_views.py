from .test_abstract import AbstractTest

class ViewsTest(AbstractTest):

    def test_home_page(self):
        response = self.app.get('/')
        self.assertIn(b'Datashare preview', response.body)
