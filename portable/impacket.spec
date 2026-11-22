# -*- mode: python ; coding: utf-8 -*-

# Imports
import ast
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata


PROJECT_ROOT = Path(SPEC).resolve().parents[1]
EXCLUDED_TOOLS = {'sniff', 'split'}
LEGACY_IMPORTS = {'urllib2'}
scripts = [
    script
    for script in sorted((PROJECT_ROOT / 'examples').glob('*.py'))
    if script.stem not in EXCLUDED_TOOLS
]

datas = [(str(PROJECT_ROOT / 'LICENSE'), '.')]
datas.extend((str(script), 'examples') for script in scripts)
datas.extend(copy_metadata('impacket'))
for package in ('flask', 'impacket', 'ldapdomaindump'):
    datas.extend(collect_data_files(package))

hiddenimports = []
for script in scripts:
    tree = ast.parse(script.read_text(encoding='utf-8'), filename=str(script))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hiddenimports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            hiddenimports.append(node.module)
hiddenimports = [module for module in hiddenimports if module not in LEGACY_IMPORTS]
for package in (
        'Cryptodome',
        'OpenSSL',
        'cryptography',
        'dns',
        'impacket',
        'ldap3',
        'ldapdomaindump',
        'pyasn1',
        'pyasn1_modules',
        'pyreadline3'):
    hiddenimports.extend(collect_submodules(package))
hiddenimports = sorted(set(hiddenimports))

analysis = Analysis(
    [str(PROJECT_ROOT / 'portable' / 'impacket_cli.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pcapy'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name='impacket',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

distribution = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='impacket',
)
