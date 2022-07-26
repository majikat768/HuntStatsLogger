# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['./src/main.py'],
    pathex=[],
    binaries=[],
    datas=[('./assets', 'assets/'), ('./src/', '.')],
    hiddenimports=['xmltodict','PyQt6','pyqtgraph','pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt6','pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt6','pyqtgraph.console.template_pyside2','pyqtgraph.imageview.ImageViewTemplate_pyside2','pyqtgraph.imageview.ImageViewTemplate_pyqt6'],
    hookspath=[],
    hooksconfig={},
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
    name='HuntStatsLogger-console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./assets/icons/hsl.ico'
)