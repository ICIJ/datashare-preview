from .test_abstract import AbstractTest

class ViewsTest(AbstractTest):

    def test_home_page(self):
        response = self.client.get('/')
        self.assertIn('Datashare preview', response.text)
