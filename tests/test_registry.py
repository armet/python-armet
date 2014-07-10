from armet.registry import Registry


class TestRegistry:

    def setup(self):
        self.registry = Registry()
        for x in range(10):
            self.registry.register("obj_%d" % x, name="test_%d" % x)

    def test_register_with_same_name(self):
        reg = self.registry

        reg.register("")



