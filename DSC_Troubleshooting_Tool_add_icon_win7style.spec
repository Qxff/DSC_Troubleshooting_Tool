# -*- mode: python -*-

block_cipher = None


a = Analysis(['DSC_Troubleshooting_Tool.py'],
             pathex=['C:\\Users\\g800472\\Desktop\\Python\\DSS_tools\\DSC_Troubleshooting_Tool'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('PyQt5/Qt/plugins/styles/qwindowsvistastyle.dll', 'C:\\Users\g800472\AppData\Local\Programs\Python\Python36-32\Lib\site-packages\PyQt5\Qt\plugins\styles\qwindowsvistastyle.dll', 'BINARY')],
          name='DSC_Troubleshooting_Tool_Suite',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,icon='C:\\Users\g800472\Desktop\Python\DSS_tools\DSC_Troubleshooting_Tool\dsc.ico')
