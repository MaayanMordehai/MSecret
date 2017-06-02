#
## @package MSecret.install install module.
## @file install.py Implementation of @ref MSecret.install
#


import wx
import os
import _winreg


## descryption for the installion frame
DESCRIPTION = """MSecret is an encryption program for windows.
Features include the ability to encrypt with a password
(to <filename>.MSecret) and delete safely any file,
decrypt '.MSecret' files. also the program inclode special
state in which the user creates a directory with a password,
all the files and the file names are encrypted and the acsses
to the decrypted files and file names is from the program.


PLEASE RESTART YOUR COMPUTER AFTER PRESSING INSTALL! :)

created by Maayan Mordehai
"""
## environment varibles path in registry
ENVIRONMENT_PATH = "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
## path for directory encryption in registry
DIRECTORY_PATH_EN = "Directory\shell\Encrypt\command"
## path for directory mode in registry
DIRECTORY_PATH_MODE = "Directory\shell\Open Directory Mode\command"
## path for directory decryption in registry
DIRECTORY_PATH_DEC = "Directory\shell\Decrypt\command"
## path for file encryption in registry
ENCRYPT_PATH = "*\shell\Encrypt\command"
## running encryption in registry
RUN_ENCRYPT = "c:\python27\pythonw -m MSecret.action --command encrypt --src-file %1"
## path for file decryption in registry
DECRYPT_PATH = "MSecretfile\shell\Decrypt\command"
## file encrypted ending
DECRYPT_ENDING = '.MSecret'
## file encrypted ending handling in registry
DECRYPT_SEND_TO = 'MSecretfile'
## running decryption in registry
RUN_DECRYPT = "c:\\python27\\pythonw -m MSecret.action --command decrypt --src-file %1"
## path for delete (files) in registry
DELETE_PATH = "*\\shell\Special Delete\command"
## running delete in registry
RUN_DELETE = "c:\\python27\\pythonw -m MSecret.action --command delete --src-file %1"
## PYTHONPATH
PYTHONPATH = "PYTHONPATH"
## running directory mode in registry dir
RUN_DIR_WITH_DIR = "c:\\python27\\pythonw -m MSecret.action --command directory --src-file %1" 


## Installation.
#
# creates installion frame and handling installion
#
class Installation(wx.Frame):

    ## Constructor
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

    ## installing MSecret
    # @param event (event) event.
    #
    # will be applied only if button install pressed
    #
    def install(self, event):
        path = os.path.realpath(__file__)
        dir = self._dup_slash(os.path.dirname(path))
        try:
            try:
                registry_key = _winreg.OpenKey(
                    _winreg.HKEY_LOCAL_MACHINE,
                    ENVIRONMENT_PATH,
                    0,
                    _winreg.KEY_ALL_ACCESS,
                )

            except WindowsError:
                registry_key = _winreg.CreateKey(
                    _winreg.HKEY_LOCAL_MACHINE,
                    ENVIRONMENT_PATH,
                )

            try:
                value, _ = _winreg.QueryValueEx(registry_key, PYTHONPATH)
                dir = "%s;%s" % (value, dir)
            except WindowsError:
                pass #there is not PYTHONPATH varible yet.

            _winreg.SetValueEx(
                registry_key,
                PYTHONPATH,
                0,
                _winreg.REG_EXPAND_SZ,
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
                DIRECTORY_PATH_EN,
                _winreg.REG_SZ,
                RUN_ENCRYPT,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DIRECTORY_PATH_MODE,
                _winreg.REG_SZ,
                RUN_DIR_WITH_DIR,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DIRECTORY_PATH_DEC,
                _winreg.REG_SZ,
                RUN_DECRYPT,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DECRYPT_PATH,
                _winreg.REG_SZ,
                RUN_DECRYPT,
            )
            _winreg.SetValue(
                _winreg.HKEY_CLASSES_ROOT,
                DECRYPT_ENDING,
                _winreg.REG_SZ,
                DECRYPT_SEND_TO,
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

    ## duplicate \.
    # @param string (string) string.
    #
    def _dup_slash(self, string):
        count = 0
        for ch in string:
            if ch == '\\':
                stri = "%s\%s" % (string[:count], string[count:])
            count += 1
        return stri

    ## exiting
    #@param event (event) event
    #
    #will be applied only if exit was pressed
    #
    def OnExit(self, event):
        self.Destroy()


## Main implementation.
def main():
    app = wx.App(False)
    frame = Installation()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    main()
