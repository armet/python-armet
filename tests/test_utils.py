from pytest import mark
from armet import utils


@mark.bench("utils.dasherize", iterations=100000)
class TestDasherize:

    def test_simple(self):
        text = utils.dasherize("ContactPhoto")

        assert text == "contact-photo"
