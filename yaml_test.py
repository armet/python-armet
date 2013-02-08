import yaml


print yaml.load
someyaml = {}
someyaml['crap'] = 'Something'
someyaml['stuff'] = 'crap'
print yaml.safe_load("""something: other
shit: stuff""")

        # except Exception:
        #     # Something unexpected; no YAML could be decoded
        #     raise Exception()


# d = Decoder()

# d.decode()

"""something: other
shit: stuff"""
