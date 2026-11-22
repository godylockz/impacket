#!/usr/bin/env python3
# -- coding: utf-8 --
"""Tests for the portable multicall entry point and plugin manifests."""

# Imports
import runpy
import sys
import unittest
from pathlib import Path
from unittest import mock

from impacket.examples.ntlmrelayx.attacks import ATTACK_PLUGIN_MODULES
from impacket.examples.ntlmrelayx.clients import CLIENT_PLUGIN_MODULES
from impacket.examples.ntlmrelayx.servers.socksplugins import SOCKS_PLUGIN_MODULES
from portable import impacket_cli


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PortableCliTests(unittest.TestCase):

    def test_discovery_matches_supported_examples(self):
        actual = {script.stem for script in impacket_cli.discover_tools().values()}
        expected = {
            script.stem for script in (PROJECT_ROOT / 'examples').glob('*.py')
            if script.stem not in impacket_cli.EXCLUDED_TOOLS
        }
        self.assertEqual(expected, actual)

    def test_dispatch_sets_and_restores_argv(self):
        script = PROJECT_ROOT / 'examples' / 'secretsdump.py'
        original_argv = sys.argv
        invoked_argv = []

        def capture_argv(*_args, **_kwargs):
            invoked_argv.append(list(sys.argv))

        with mock.patch.object(runpy, 'run_path', side_effect=capture_argv) as run_path:
            self.assertEqual(0, impacket_cli.dispatch(script, ['--help']))
            run_path.assert_called_once_with(str(script), run_name='__main__')
            self.assertEqual([['secretsdump.py', '--help']], invoked_argv)
        self.assertIs(original_argv, sys.argv)

    def test_tool_lookup_is_case_insensitive(self):
        with mock.patch.object(impacket_cli, 'dispatch', return_value=0) as dispatch:
            self.assertEqual(0, impacket_cli.main(['SeCrEtSdUmP', '--help']))
        self.assertEqual('secretsdump', dispatch.call_args.args[0].stem)
        self.assertEqual(['--help'], dispatch.call_args.args[1])

    def test_unknown_tool_returns_usage_error(self):
        with mock.patch('sys.stderr'):
            self.assertEqual(2, impacket_cli.main(['not-an-impacket-tool']))


class PluginManifestTests(unittest.TestCase):

    def assert_manifest_matches_directory(self, relative_directory, manifest):
        directory = PROJECT_ROOT / relative_directory
        modules = {path.stem for path in directory.glob('*.py') if path.name != '__init__.py'}
        self.assertEqual(modules, set(manifest))

    def test_client_manifest(self):
        self.assert_manifest_matches_directory('impacket/examples/ntlmrelayx/clients', CLIENT_PLUGIN_MODULES)

    def test_attack_manifest(self):
        self.assert_manifest_matches_directory('impacket/examples/ntlmrelayx/attacks', ATTACK_PLUGIN_MODULES)

    def test_socks_manifest(self):
        self.assert_manifest_matches_directory(
            'impacket/examples/ntlmrelayx/servers/socksplugins', SOCKS_PLUGIN_MODULES)


if __name__ == '__main__':
    unittest.main()
