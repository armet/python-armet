from pytest import mark
from armet import utils


@mark.bench("utils.dasherize", iterations=100000)
class TestDasherize:

    def test_from_pascal_case(self):
        text = utils.dasherize("ContactPhoto")

        assert text == "contact-photo"

    def test_from_camel_case(self):
        text = utils.dasherize("contactPhoto")

        assert text == "contact-photo"

    def test_from_underscores(self):
        text = utils.dasherize("contact_photo")

        assert text == "contact-photo"

    def test_from_dashed(self):
        text = utils.dasherize("contact-photo")

        assert text == "contact-photo"
