from afl_utils import afl_multicore

try:
    import simplejson as json
except ImportError:
    import json
import os
import unittest

test_conf_settings = {
    'afl_margs': '-T banner',
    'dumb': True,
    'timeout': '200+',
    'dict': 'dict/target.dict',
    'file': '@@',
    'interactive': True,
    'target': '/usr/bin/target',
    'input': './in',
    'cmdline': '-a -b -c -d',
    'session': 'SESSION',
    'qemu': True,
    'output': './out',
    'dirty': True,
    'mem_limit': '150',
    'slave_only': False,
    'environment': [
        'AFL_PERSISTENT=1'
    ]
}

test_conf_settings1 = {
    'interactive': False,
    'target': '/usr/bin/target',
    'input': './in',
    'cmdline': '-a -b -c -d',
    'session': 'SESSION',
    'output': './out',
    'slave_only': True,
    'environment': [
        'AFL_PERSISTENT=1'
    ]
}

test_conf_settings2 = {
    'target': '/usr/bin/target',
    'input': './in',
    'cmdline': '-a -b -c -d',
    'output': './out'
}

test_conf_settings3 = {
    'afl_margs': '-T banner',
    'dumb': True,
    'timeout': '200+',
    'dict': 'dict/target.dict',
    'file': 'sample_file',
    'interactive': True,
    'target': '/usr/bin/target',
    'input': './in',
    'cmdline': '-a -b -c -d',
    'session': 'SESSION',
    'qemu': True,
    'output': './out',
    'dirty': 'on',
    'mem_limit': '150'
}

test_afl_cmdline = [
    '-f', '@@', '-t', '200+', '-m', '150', '-Q', '-d', '-n', '-x', 'dict/target.dict', '-T banner', '-i',
    './in', '-o', './out'
]

test_afl_cmdline2 = [
    '-i', './in', '-o', './out'
]

test_afl_cmdline21 = [
   '-i', './in', '-o', './out'
]

test_afl_cmdline3 = [
    '-f', 'sample_file_027', '-t', '200+', '-m', '150', '-Q', '-d', '-n', '-x', 'dict/target.dict', '-T banner', '-i',
    './in', '-o', './out'
]


class AflMulticoreTestCase(unittest.TestCase):
    def setUp(self):
        # Use to set up test environment prior to test case
        # invocation
        pass

    def tearDown(self):
        # Use for clean up after tests have run
        if os.path.exists('/tmp/afl_multicore.PGID.unittest_sess_01'):
            os.remove('/tmp/afl_multicore.PGID.unittest_sess_01')

    def test_show_info(self):
        self.assertIsNone(afl_multicore.show_info())

    def test_read_config(self):
        conf_settings = afl_multicore.read_config('testdata/afl-multicore.conf.test')
        self.assertDictEqual(test_conf_settings, conf_settings)

        conf_settings = afl_multicore.read_config('testdata/afl-multicore.conf1.test')
        self.assertDictEqual(test_conf_settings1, conf_settings)

        conf_settings = afl_multicore.read_config('testdata/afl-multicore.conf2.test')
        self.assertDictEqual(test_conf_settings2, conf_settings)

        # Config file not found
        with self.assertRaises(SystemExit) as se:
            afl_multicore.read_config('invalid-config-file')
        self.assertEqual(se.exception.code, 1)

        # JSON decode error
        with self.assertRaises(json.decoder.JSONDecodeError):
            afl_multicore.read_config('testdata/afl-multicore.conf.invalid00.test')

    def test_afl_cmdline_from_config(self):
        afl_cmdline = afl_multicore.afl_cmdline_from_config(test_conf_settings, 12)
        self.assertEqual(afl_cmdline, test_afl_cmdline)

        afl_cmdline = afl_multicore.afl_cmdline_from_config(test_conf_settings2, 1)
        self.assertEqual(afl_cmdline, test_afl_cmdline2)

        afl_cmdline = afl_multicore.afl_cmdline_from_config(test_conf_settings2, 4)
        self.assertEqual(afl_cmdline, test_afl_cmdline21)

        afl_cmdline = afl_multicore.afl_cmdline_from_config(test_conf_settings3, 27)
        self.assertEqual(afl_cmdline, test_afl_cmdline3)

    def test_check_screen(self):
        if os.environ.get('STY'):
            sty = os.environ['STY']
            self.assertTrue(afl_multicore.check_screen())
            os.environ.pop('STY')
            self.assertFalse(afl_multicore.check_screen())
            os.environ['STY'] = sty
        else:
            self.assertFalse(afl_multicore.check_screen())
            os.environ['STY'] = 'screen'
            self.assertTrue(afl_multicore.check_screen())
            os.environ.pop('STY')
            self.assertFalse(afl_multicore.check_screen())

    def test_setup_screen_env(self):
        # Skip test for screen environment variable setting for now
        pass

    def test_setup_screen(self):
        # Skip test for screen window setup for now
        pass
    #     if afl_multicore.check_screen():
    #         env_list = [
    #             'test_env_var1=1',
    #             'test_env_var2=2',
    #             'test_env_var3=3',
    #             'test_env_var4=4',
    #             'test_env_var5=5'
    #         ]
    #         afl_multicore.setup_screen(1, env_list)
    #
    #         subprocess.Popen("screen -X select 1".split())
    #
    #         for e in env_list:
    #             self.assertEqual(os.environ[e[0]], e[1])
    #
    #         subprocess.Popen("logout".split())
    #     else:
    #         print("Not in a screen session, will skip test_setup_screen_env!")

    def test_sigint_handler(self):
        with self.assertRaises(SystemExit) as se:
            afl_multicore.sigint_handler(0, 0)
        self.assertEqual(se.exception.code, 0)

    def test_build_target_cmd(self):
        # invalid test
        conf_settings = {
            'target': 'testdata/dummy_process/invalid_process',
            'cmdline': ''
        }
        with self.assertRaises(SystemExit) as se:
            afl_multicore.build_target_cmd(conf_settings)
        self.assertEqual(1, se.exception.code)

        # valid test
        conf_settings = {
            'target': '/bin/sh',
            'cmdline': '--some-opt'
        }
        self.assertEqual('/bin/sh --some-opt', afl_multicore.build_target_cmd(conf_settings))

    def test_build_master_cmd(self):
        conf_settings = {
            'session': 'SESSION',
            'file': 'cur_input'
        }
        target_cmd = 'testdata/dummy_process/invalid_proc --some-opt %%'
        master_cmd = afl_multicore.afl_path + ' -f cur_input_000 -M SESSION000 -- ' + target_cmd.replace('%%', conf_settings['file']+'_000')

        self.assertEqual(master_cmd, afl_multicore.build_master_cmd(conf_settings, target_cmd))

    def test_build_slave_cmd(self):
        conf_settings = {
            'session': 'SESSION',
            'file': 'cur_input'
        }
        target_cmd = 'testdata/dummy_process/invalid_proc --some-opt %%'
        slave_num = 3
        slave_cmd = afl_multicore.afl_path + ' -f cur_input_003 -S SESSION003 -- ' + target_cmd.replace("%%", conf_settings['file']+'_003')

        self.assertEqual(slave_cmd, afl_multicore.build_slave_cmd(conf_settings, slave_num, target_cmd))

    def test_write_pgid_file(self):
        # negative test
        conf_settings = {
            'session': 'unittest_sess_01',
            'output': 'testdata/output',
            'interactive': True,
        }
        self.assertIsNone(afl_multicore.write_pgid_file(conf_settings))
        self.assertIsNot(True, os.path.exists('/tmp/afl_multicore.PGID.unittest_sess_01'))

        # positive test
        conf_settings = {
            'session': 'unittest_sess_01',
            'output': 'testdata/output',
            'interactive': False,
        }
        self.assertIsNone(afl_multicore.write_pgid_file(conf_settings))
        self.assertIs(True, os.path.exists('/tmp/afl_multicore.PGID.unittest_sess_01'))

    def test_get_slave_count(self):
        # negative test
        conf_settings = {
        }
        command = 'start'
        self.assertEqual((1, 1), afl_multicore.get_slave_count(command, conf_settings))

        # positive test
        conf_settings = {
            'session': 'fuzz',
            'output': 'testdata/sync',
            'slave_only': False,
        }
        command = 'add'
        self.assertEqual((0, 2), afl_multicore.get_slave_count(command, conf_settings))

    def test_get_job_counts(self):
        jobs_arg = "23"
        expected = (23, 0)
        self.assertEqual(afl_multicore.get_job_counts(jobs_arg), expected)

        jobs_arg = "23,0"
        expected = (23, 0)
        self.assertEqual(afl_multicore.get_job_counts(jobs_arg), expected)

        jobs_arg = "12,5"
        expected = (12, 5)
        self.assertEqual(afl_multicore.get_job_counts(jobs_arg), expected)

    def test_has_master(self):
        # positive test
        conf_settings = {
        }
        self.assertTrue(afl_multicore.has_master(conf_settings, 0))

        conf_settings = {
            'session': 'fuzz',
            'output': 'testdata/sync',
            'slave_only': False,
        }
        self.assertTrue(afl_multicore.has_master(conf_settings, 0))

        # negative test
        self.assertFalse(afl_multicore.has_master(conf_settings, 1))

        conf_settings = {
            'session': 'fuzz',
            'output': 'testdata/sync',
            'slave_only': True,
        }
        self.assertFalse(afl_multicore.has_master(conf_settings, 0))
        self.assertFalse(afl_multicore.has_master(conf_settings, 2))

    def test_main(self):
        # we're only going to test some error cases
        # invalid invocation (Argparser failure)
        with self.assertRaises(SystemExit) as se:
            afl_multicore.main(['afl-multicore', '-c', 'invalid.conf', '--invalid-opt'])
        self.assertEqual(2, se.exception.code)

        # test run
        with self.assertRaises(SystemExit) as se:
            afl_multicore.main(['afl-multicore', '-c', 'testdata/afl-multicore.conf.test', '-t', 'start', '4'])
        self.assertEqual(1, se.exception.code)

        # resume run
        with self.assertRaises(SystemExit) as se:
            afl_multicore.main(['afl-multicore', '-c', 'testdata/afl-multicore.conf.test', 'resume', '4'])
        self.assertEqual(1, se.exception.code)
