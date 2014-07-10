from armet.registry import Registry
import pytest


class TestRegistry:

    def setup(self):
        self.registry = Registry()
        for x in range(5):
            self.registry.register("obj_%d" % x, name="test_%d" % x)
            self.registry.register("obj_%d" % x, name2="test_%d" % x)

    def test_register_and_find(self):

        # Test that fancy new register decorator
        @self.registry.register(name="test_12")
        def test_registry_decorator():
            return "Example_obj"

        self.registry.register("Example_obj2", name="test_13")

        # test_registry_decorator()

        assert self.registry.find(name="test_12") is test_registry_decorator

    def test_raise_registry_exceptions(self):
        # with pytest.raises(TypeError):
        #     @self.registry.register(None, name="not_valid")

        with pytest.raises(TypeError):
            self.registry.find(name="this", multiple_kwargs="not_valid")

        # Test the not-found exception in find, raises key-error, returns None.
        assert self.registry.find(some_property="non_existant") is None

    def test_remove(self):
        # Test removing with just the object
        # self.registry.remove("obj_1")
        # assert self.registry.find(name="test_1") is None
        # # assert that every single reference is removed
        # assert self.registry.find(name2="test_1") is None

        # Test removing with just kwargs:
        self.registry.remove(name="test_2")
        assert self.registry.find(name="test_2") is None
        # assert that every single reference is removed
        assert self.registry.find(name2="test_2") is None
