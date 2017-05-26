import wx
import os
import _winreg


QUESTION = "Are you sure you want to UNINSTALL?"
ENVIRONMENT_PATH = "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
PATH_ALL_FILES = "*\shell"
PATH_MSECRET_FILE = ""
ENCRYPT = ("Encrypt", "command")
DELETE = ("Special Delete", "command")
PYTHONPATH = "PYTHONPATH"
DECRYPT = ("MSecretfile", "shell", "Decrypt", "command")
DECRYPT_ENDING = '.MSecret'


def Uninstall(parent, question, caption='Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result


def dup_slash(string):
    count = 0
    for ch in string:
        if ch == '\\':
            string = "%s\%s" % (string[:count], string[count:])
        count += 1
    return string


def main():
    app = wx.App()
    uninstall = Uninstall(None, QUESTION)
    app.MainLoop()
    if uninstall:
        try:
            registry_key = _winreg.OpenKey(
                _winreg.HKEY_CLASSES_ROOT,
                PATH_ALL_FILES,
                0,
                _winreg.KEY_ALL_ACCESS,
            )
            try:
                _winreg.DeleteKey(registry_key, "%s\%s" % (ENCRYPT[0], ENCRYPT[1]))
            except WindowsError:
                print "%s\%s doesn't exist in regedit" % (ENCRYPT[0], ENCRYPT[1])
            try:
                _winreg.DeleteKey(registry_key, ENCRYPT[0])
            except WindowsError:
                print "%s doesn't exist in regedit" % ENCRYPT[0]
            try:
                _winreg.DeleteKey(registry_key, "%s\%s" % (DELETE[0], DELETE[1]))
            except WindowsError:
                print "%s\%s doesn't exist in regedit" % (DELETE[0], DELETE[1])
            try:
                _winreg.DeleteKey(registry_key, DELETE[0])
            except WindowsError:
                print "%s doesn't exist in regedit" % DELETE[0]

            decrypt_key = _winreg.OpenKey(
                _winreg.HKEY_CLASSES_ROOT,
                PATH_MSECRET_FILE,
                0,
                _winreg.KEY_ALL_ACCESS,
            )
            try:
                _winreg.DeleteKey(
                    decrypt_key,
                    DECRYPT_ENDING,
                )
            except WindowsError:
                print "%s doesn't exist in regedit" % DECRYPT_ENDING
            try:
                _winreg.DeleteKey(
                    decrypt_key,
                    "%s\%s\%s\%s" % (
                        DECRYPT[0],
                        DECRYPT[1],
                        DECRYPT[2],
                        DECRYPT[3],
                    ),
                )
            except WindowsError:
                print "%s\%s\%s\%s doesn't exist in regedit" % (
                    DECRYPT[0],
                    DECRYPT[1],
                    DECRYPT[2],
                    DECRYPT[3],
                )
            try:
                _winreg.DeleteKey(
                    decrypt_key,
                    "%s\%s\%s" % (
                        DECRYPT[0],
                        DECRYPT[1],
                        DECRYPT[2],
                    )
                )
            except WindowsError:
                print "%s\%s\%s doesn't exist in regedit" % (
                    DECRYPT[0],
                    DECRYPT[1],
                    DECRYPT[2],
                )
            try:
                _winreg.DeleteKey(
                    decrypt_key,
                    "%s\%s" % (
                        DECRYPT[0],
                        DECRYPT[1],
                    )
                )
            except WindowsError:
                print "%s\%s doesn't exist in regedit" % (
                    DECRYPT[0],
                    DECRYPT[1],
                )
            try:
                _winreg.DeleteKey(
                    decrypt_key,
                    DECRYPT[0],
                )
            except WindowsError:
                print "%s doesn't exist in regedit" % (
                    DECRYPT[0],
                )

            path = os.path.realpath(__file__)
            dir = dup_slash(os.path.dirname(path))
            pythonpath_key = _winreg.OpenKey(
                _winreg.HKEY_LOCAL_MACHINE,
                ENVIRONMENT_PATH,
                0,
                _winreg.KEY_ALL_ACCESS,
            )
            try:
                value, _ = _winreg.QueryValueEx(pythonpath_key, PYTHONPATH)
                paths = value.split(';')
                if dir in paths:
                    paths.remove(dir)
                if paths:
                    _winreg.SetValueEx(
                        pythonpath_key,
                        PYTHONPATH,
                        0,
                        _winreg.REG_SZ,
                        ';'.join(paths),
                    )
                else:
                    _winreg.DeleteValue(pythonpath_key, PYTHONPATH)
            except WindowsError:
                print "there is not PYTHONPATH varible"
        except:
            wx.MessageBox(
                "sorry, can't uninstall",
                "error",
                wx.ICON_ERROR,
            )


if __name__ == '__main__':
    main()
