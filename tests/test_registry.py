from armet.registry import Registry
import pytest


class TestRegistry:

    def setup(self):
        self.registry = Registry()
        for x in range(5):
            self.registry.register("obj_%d" % x, name="test_%d" % x)
            self.registry.register("obj_%d" % x, name2="test_%d" % x)

    def test_register_decorator(self):
        @self.registry.register(name="test_12")
        def test_registry_decorator():
            pass

        assert self.registry.find(name="test_12") is test_registry_decorator

    def test_register_none(self):
        with pytest.raises(TypeError):
            self.registry.register(name="not_valid")(None)

    def test_rfind(self):
        x = self.registry.rfind("obj_1", "name")[0]

        assert x == "test_1"

    def test_find_multiple(self):
        with pytest.raises(TypeError):
            self.registry.find(name="this", multiple_kwargs="not_valid")

    def test_find_from_fallback(self):
        # Test the not-found exception in find, raises key-error, returns None.
        fallback = Registry()
        fallback.register("fallback_obj", name="fallback")
        self.registry.fallback = fallback

        assert self.registry.find(name="fallback") == "fallback_obj"

    def test_remove_object(self):
        # Test removing with just the object
        self.registry.remove("obj_1")
        assert self.registry.find(name="test_1") is None

        # assert that every single reference is removed
        assert self.registry.find(name2="test_1") is None

    def test_remove_keyword(self):
        # Test removing with just kwargs:
        self.registry.remove(name="test_2")

        assert self.registry.find(name="test_2") is None

        # assert that every single reference is removed
        assert self.registry.find(name2="test_2") is None

        self.registry.remove(name="test_3", name2="test_3")

        assert self.registry.find(name2="test_3") is None

    def test_remove_empty_key(self):
        # Test removing the entire "test" key if it holds no items
        self.registry.register("obj_1", test="test_1")
        self.registry.remove(test="test_1")

        assert self.registry.map.get("test") is None

        # Test removing a non-existing value
        self.registry.remove(non_existant="value")
