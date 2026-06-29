# asteria.spec
block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['C:\\asteria'],
    binaries=[],
    datas=[
        ('app/assets/asteria.ico', 'assets'),
        ('app/services/notificationSound.wav', 'services'),
        ('app/services/prioritySound.wav', 'services'),
    ],
    hiddenimports=[
        'plyer.platforms.win.notification',
        'pkg_resources.py2_compat',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Asteria',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no console window
    icon='app/assets/asteria.ico',
)