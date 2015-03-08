import os, sys

from flask import Flask, url_for


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_ui(object):
    def setup_method(self, method):
        pass
        from core import Base
        Base.BASE_PREFIX = 'test'
#        app = Flask(__name__)
        import ui.ui
        self.app_test = ui.ui.app.test_client()
#        app_api = restful.Api(app)
#        import api.test
#        api.test.add_test(app_api, root='/', version='test')
#        self.app_test = app.test_client()


    def teardown_method(self, method):
        from core import Base
        from core.Index import Index
        from core.Test import Test
        from core.Status import Status
        from core.TestType import TestType
        Base.Base().get_base()[Index.collection].drop()
        Base.Base().get_base()[Test.collection].drop()
        Base.Base().get_base()[Status.collection].drop()
        Base.Base().get_base()[TestType.collection].drop()

    def test_get_index(self):
        rv = self.app_test.get('/ui')
        assert rv.status_code == 200

    def test_js(self):
        rv = self.app_test.get('/ui/js/not_existing.js')
        assert rv.status_code == 404
        rv = self.app_test.get('/ui/js/app.js')
        assert rv.status_code == 200

    def test_css(self):
        rv = self.app_test.get('/ui/css/not_existing.css')
        assert rv.status_code == 404
        rv = self.app_test.get('/ui/css/style.css')
        assert rv.status_code == 200
