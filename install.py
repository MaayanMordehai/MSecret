import wx
import os
import subprocess
import _winreg


DESCRIPTION = """MSecret is an encryption program for windows.
Features include the ability to encrypt with a password
(to <filename>.MSecret) and delete safely any file,
decrypt '.MSecret' files. also the program inclode special
state in which the user creates a directory with a password,
all the files and the file names are encrypted and the acsses
to the decrypted files and file names is from the program.
"""
ENVIRONMENT_PATH = "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
ENCRYPT_PATH = "*\shell\Encrypt\command"
RUN_ENCRYPT = "python -m MSecret.action --command encrypt --src-file %1"
DECRYPT_PATH = "MSecretfile\shell\Decrypt\command"
RUN_DECRYPT = "python -m MSecret.action --command decrypt --src-file %1"
DELETE_PATH = "*\\shell\Special Delete\command"
RUN_DELETE = "python -m MSecret.action --command delete --src-file %1"
PYTHONPATH = "PYTHONPATH"


class Installation(wx.Frame):
    def __init__(self):

        wx.Frame.__init__(
            self,
            parent=None,
            title="MSecret Installation"
        )

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox0 = wx.BoxSizer(wx.HORIZONTAL)

        panel = wx.Panel(self)
        title = wx.StaticText(
            panel,
            -1,
            'MSecret 1.0',
            style=wx.ALIGN_CENTER
        )
        font = wx.Font(
            16,
            wx.SWISS,
            wx.NORMAL,
            wx.FONTWEIGHT_BOLD,
            False,
            u'Comic Sans MS',
        )
        title.SetFont(font)
        text = wx.StaticText(
            panel,
            -1,
            DESCRIPTION,
            style=wx.ALIGN_CENTER
        )
        font1 = wx.Font(
            10,
            wx.SWISS,
            wx.NORMAL,
            wx.NORMAL,
            False,
            u'Comic Sans MS',
        )
        text.SetFont(font1)
        btn = wx.Button(panel, label="install")

        hbox0.Add(
            title,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5
        )
        hbox.Add(
            text,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5,
        )
        hbox1.Add(
            btn,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5
        )

        vbox.Add(
            hbox0,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5,
        )
        vbox.Add(
            hbox,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5,
        )
        vbox.Add(
            hbox1,
            proportion=1,
            flag=wx.CENTER | wx.ALL,
            border=5
        )
        panel.SetSizer(vbox)
        vbox.SetSizeHints(self)
        self.Centre()
        btn.Bind(
            wx.EVT_BUTTON,
            self.install,
        )
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def install(self, event):
        path = os.path.realpath(__file__)
        dir = self._dup_slash(os.path.dirname(path))
        
        try:
            try:
                registry_key = _winreg.OpenKey(
                    _winreg.HKEY_CURRENT_USER,
                    ENVIRONMENT_PATH,
                    0,
                    _winreg.KEY_ALL_ACCESS,
                )
                print "hhhhhh"
            except WindowsError:
                print "here"
                registry_key = _winreg.CreateKey(
                    _winreg.HKEY_CURRENT_USER,
                    ENVIRONMENT_PATH,
                )

            try:
                value, _ = _winreg.QueryValueEx(registry_key, PYTHONPATH)
                dir = "%s;%s" % (value, dir)
                print dir
            except WindowsError:
                pass
            _winreg.SetValueEx(
                registry_key,
                PYTHONPATH,
                0,
                _winreg.REG_SZ,
                dir,
            )
            _winreg.CloseKey(registry_key)
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                ENCRYPT_PATH,
                _winreg.REG_SZ,
                RUN_ENCRYPT,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DECRYPT_PATH,
                _winreg.REG_SZ,
                RUN_DECRYPT,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DELETE_PATH,
                _winreg.REG_SZ,
                RUN_DELETE,
            )
        except:
            wx.MessageBox(
                "sorry, can't install",
                "error",
                wx.ICON_ERROR,
            )
            raise
        self.Destroy()

    def _dup_slash(self, string):
        count = 0
        for ch in string:
            if ch == '\\':
                string = "%s\%s" % (string[:count], string[count:])
            count += 1
        return string

    def OnExit(self, event):
        self.Destroy()


def main():
    app = wx.App(False)
    frame = Installation()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()

