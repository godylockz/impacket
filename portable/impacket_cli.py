#!/usr/bin/env python3
# -- coding: utf-8 --
"""Multicall entry point for the portable Impacket distribution."""

# Imports
import ast
import runpy
import sys
import tokenize
from pathlib import Path

from impacket import version


EXCLUDED_TOOLS = {
    'sniff': 'deprecated and requires the optional native pcapy dependency',
    'split': 'deprecated and requires the optional native pcapy dependency',
}

EXPECTED_CLIENT_PLUGINS = {
    'DCSYNC', 'HTTP', 'HTTPS', 'IMAP', 'IMAPS', 'LDAP', 'LDAPS', 'MSSQL', 'RPC', 'SMB', 'SMTP', 'WINRMS',
}
EXPECTED_ATTACK_PLUGINS = {
    'DCSYNC', 'HTTP', 'HTTPS', 'IMAP', 'IMAPS', 'LDAP', 'LDAPS', 'MSSQL', 'RPC', 'SMB', 'WINRMS',
}
EXPECTED_SOCKS_PLUGINS = {
    'HTTP Socks Plugin', 'HTTPS Socks Plugin', 'IMAP Socks Plugin', 'IMAPS Socks Plugin',
    'LDAP Socks Plugin', 'LDAPS Socks Plugin', 'MSSQL Socks Plugin', 'SMB Socks Plugin', 'SMTP Socks Plugin',
}


def scripts_directory():
    """Return the trusted directory containing bundled example scripts."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        directory = Path(sys._MEIPASS) / 'examples'
    else:
        directory = Path(__file__).resolve().parents[1] / 'examples'

    if not directory.is_dir():
        raise RuntimeError('bundled Impacket scripts were not found at %s' % directory)
    return directory


def discover_tools(directory=None):
    """Return a case-insensitive command map for bundled scripts."""
    directory = directory or scripts_directory()
    tools = {}
    for script in sorted(directory.glob('*.py'), key=lambda path: path.stem.lower()):
        if script.stem in EXCLUDED_TOOLS:
            continue
        key = script.stem.lower()
        if key in tools:
            raise RuntimeError('case-insensitive tool name collision: %s and %s' % (tools[key].stem, script.stem))
        tools[key] = script
    return tools


def dispatch(script, arguments):
    """Execute one trusted bundled script with its original argument handling."""
    original_argv = sys.argv
    sys.argv = [script.name, *arguments]
    try:
        runpy.run_path(str(script), run_name='__main__')
    finally:
        sys.argv = original_argv
    return 0


def run_self_test():
    """Validate bundled scripts, runtime dependencies, and relay plugin registries."""
    tools = discover_tools()
    if not tools:
        raise RuntimeError('no bundled Impacket commands were found')

    for script in tools.values():
        with tokenize.open(script) as source_file:
            ast.parse(source_file.read(), filename=str(script))

    required_modules = (
        'Cryptodome',
        'OpenSSL',
        'asyncore',
        'charset_normalizer',
        'cryptography',
        'dns',
        'flask',
        'ldap3',
        'ldapdomaindump',
        'pyasn1',
        'pyasn1_modules',
        'socks',
    )
    for module_name in required_modules:
        __import__(module_name)
    if sys.platform == 'win32':
        __import__('pyreadline3')

    from impacket.examples.ntlmrelayx.attacks import PROTOCOL_ATTACKS
    from impacket.examples.ntlmrelayx.clients import PROTOCOL_CLIENTS
    from impacket.examples.ntlmrelayx.servers.socksplugins import SOCKS_RELAYS

    plugin_sets = (
        ('relay clients', set(PROTOCOL_CLIENTS), EXPECTED_CLIENT_PLUGINS),
        ('relay attacks', set(PROTOCOL_ATTACKS), EXPECTED_ATTACK_PLUGINS),
        ('SOCKS plugins', {plugin.PLUGIN_NAME for plugin in SOCKS_RELAYS}, EXPECTED_SOCKS_PLUGINS),
    )
    for label, actual, expected in plugin_sets:
        if actual != expected:
            raise RuntimeError('%s mismatch: expected %r, got %r' % (label, sorted(expected), sorted(actual)))

    print('Self-test passed: %d commands and all ntlmrelayx plugins loaded.' % len(tools))
    return 0


def print_help(tools):
    print('Usage: impacket <tool> [arguments]')
    print('       impacket --list')
    print('       impacket --self-test')
    print('       impacket --version')
    print()
    print('Run "impacket <tool> --help" for tool-specific help.')
    print('%d commands are available.' % len(tools))


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    tools = discover_tools()

    if not arguments or arguments[0] in ('-h', '--help'):
        print_help(tools)
        return 0
    if arguments[0] == '--list':
        print('\n'.join(script.stem for script in tools.values()))
        return 0
    if arguments[0] == '--version':
        print(version.BANNER.strip())
        return 0
    if arguments[0] == '--self-test':
        return run_self_test()
    if arguments[0] == 'help':
        if len(arguments) == 1:
            print_help(tools)
            return 0
        arguments = [arguments[1], '--help']

    command = arguments[0].lower()
    script = tools.get(command)
    if script is None:
        print('Unknown Impacket tool: %s' % arguments[0], file=sys.stderr)
        print('Use "impacket --list" to show available tools.', file=sys.stderr)
        return 2
    return dispatch(script, arguments[1:])


if __name__ == '__main__':
    raise SystemExit(main())
