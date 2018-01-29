from errbot.backends.test import testbot
import salt_telegram


class TestSaltTelegram(object):
    extra_plugin_dir = '.'
    extra_config = {'SALT_API_URL': 'http://127.0.0.1:8080/',
                    'SALT_API_USERNAME': 'saltapi',
                    'SALT_API_PASSWORD': 'saltapi',
                    'SALT_API_EAUTH': 'pam'}

    def test_minions(self, testbot):
        testbot.setup(extra_config=self.extra_config)
        testbot.push_message('!minions')
        assert 'docker01.local' in testbot.pop_message()

    def test_glob(self, testbot):
        testbot.setup(extra_config=self.extra_config)
        testbot.push_message('!glob "docker01.*" ls')
        assert 'anaconda-ks.cfg' in testbot.pop_message()

    def test_grain(self, testbot):
        testbot.setup(extra_config=self.extra_config)
        testbot.push_message('!grain "virtual_subtype:Docker" ls')
        assert 'anaconda-ks.cfg' in testbot.pop_message()
