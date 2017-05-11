
import base64
import os
import wx
import wx.lib.dialogs

from ..common import delete
from ..common import crypte
from ..common import code_file


BLOCK_SIZE = 1024
FILE_END = '.txt'
LIMIT_CHARACTERS_TO_FILE_NAME = 31


class NameAndPassword(wx.Frame):

    def __init__(self, parent, save):
        self._save = save

        wx.Frame.__init__(
            self,
            parent,
            title='Enter Directory And Password',
        )

        self._panel = wx.Panel(self)

        self._button = wx.Button(
            self._panel,
            label='create new directory',
        )

        self._button2 = wx.Button(
            self._panel,
            label='read or edit directory',
        )

        self._lblfile = wx.StaticText(
            self._panel,
            label="directory:",
        )
        self._editfile = wx.TextCtrl(
            self._panel,
            size=(140, -1),
        )

        self._lblpassword = wx.StaticText(
            self._panel,
            label="password:",
        )
        self._editpassword = wx.TextCtrl(
            self._panel,
            style=wx.TE_PASSWORD,
            size=(140, -1),
        )

        # Set sizer for the frame, so we can change frame size to match widgets
        self._windowSizer = wx.BoxSizer()
        self._windowSizer.Add(
            self._panel,
            1,
            wx.ALL | wx.EXPAND,
        )

        # Set sizer for the panel content)
        self._sizer = wx.GridBagSizer(6, 6)
        self._sizer.Add(
            self._lblfile,
            (0, 0),
        )
        self._sizer.Add(
            self._editfile,
            (0, 1),
        )
        self._sizer.Add(
            self._lblpassword,
            (1, 0),
        )
        self._sizer.Add(
            self._editpassword,
            (1, 1),
        )
        self._sizer.Add(
            self._button2,
            (2, 0),
            flag=wx.EXPAND,
        )
        self._sizer.Add(
            self._button,
            (2, 1),
            flag=wx.EXPAND,
        )
        self._border = wx.BoxSizer()

        self._border.Add(
            self._sizer,
            1,
            wx.ALL | wx.EXPAND,
            5,
        )

        # Use the sizers
        self._panel.SetSizerAndFit(self._border)
        self.SetSizerAndFit(self._windowSizer)

        # Set event handlers
        self._button2.Bind(
            wx.EVT_BUTTON,
            self.edit_dir_button,
        )
        self._button.Bind(
            wx.EVT_BUTTON,
            self.create_dir_button,
        )
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    def edit_dir_button(self, e):
        dir = self._editfile.GetValue()
        if os.path.exists(dir):
            if os.path.isdir(dir):
                self._save.dir_name = dir
                self._save.password = self._editpassword.GetValue()
                self.Destroy()
            else:
                wx.MessageBox(
                    "file is not a directory!",
                    "error",
                    wx.ICON_ERROR,
                )
        else:
            wx.MessageBox(
                "path is not exists!",
                "error",
                wx.ICON_ERROR,
            )

    def create_dir_button(self, e):
        try:
            os.makedirs(self._editfile.GetValue())
            self._save.dir_name = self._editfile.GetValue()
            self._save.password = self._editpassword.GetValue()
            self.Destroy()
        except:
            wx.MessageBox(
                "check the path please.",
                "error",
                wx.ICON_ERROR,
            )

    def OnExit(self, event):
        self.Destroy()


class Save(object):

    def __init__(self):
        self._dir_name = None
        self._password = None

    @property
    def dir_name(self):
        return self._dir_name

    @property
    def password(self):
        return self._password

    @dir_name.setter
    def dir_name(self, name):
        self._dir_name = name

    @password.setter
    def password(self, password):
        self._password = password


class FilesAndOptions(wx.Frame):

    def __init__(self, parent, save):

        wx.Frame.__init__(self, parent, -1, save.dir_name, size=(350, 220))

        panel = wx.Panel(self, -1)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        btnPanel = wx.Panel(panel, -1)

        self._file_and_encrypted = {}
        self._list_items = []
        try:
            for name in os.listdir(save.dir_name):
                decrypted = decrypt_file_name(name, save.password)
                self._file_and_encrypted[decrypted] = name
                self._list_items.append(decrypted)
        except:
            wx.MessageBox(
                "Worng password or Wrong directory",
                "error",
                wx.ICON_ERROR
            )
            raise
        self._save = save

        self._listbox = wx.ListBox(panel, -1)
        hbox.Add(self._listbox, 1, wx.EXPAND | wx.ALL, 25)

        for file in self._list_items:
            self._listbox.Append(file)

        vbox = wx.BoxSizer(wx.VERTICAL)
        new = wx.Button(
            btnPanel,
            label='New File',
            size=(90, 30),
        )
        ren = wx.Button(
            btnPanel,
            label='Rename',
            size=(90, 30),
        )
        dlt = wx.Button(
            btnPanel,
            label='Delete',
            size=(90, 30),
        )
        viw = wx.Button(
            btnPanel,
            label='View',
            size=(90, 30),
        )
        edt = wx.Button(
            btnPanel,
            label='Edit',
            size=(90, 30),
        )

        new.Bind(wx.EVT_BUTTON, self.new_file)
        ren.Bind(wx.EVT_BUTTON, self.rename)
        dlt.Bind(wx.EVT_BUTTON, self.delete)
        viw.Bind(wx.EVT_BUTTON, self.view)
        edt.Bind(wx.EVT_BUTTON, self.edit)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.view)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        vbox.Add((-1, 25))
        vbox.Add(new)
        vbox.Add(ren, 0, wx.TOP, 5)
        vbox.Add(dlt, 0, wx.TOP, 5)
        vbox.Add(viw, 0, wx.TOP, 5)
        vbox.Add(edt, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 25)
        panel.SetSizer(hbox)

        self.Centre()
        self.Maximize(True)

    def delete(self, event):
        file_index = self._listbox.GetSelection()
        if file_index != -1:
            file = self._listbox.GetString(file_index)
            self._listbox.Delete(file_index)
            delete.delete_file_properly(
                os.path.join(
                    self._save.dir_name,
                    self._file_and_encrypted[file],
                )
            )
            self._list_items.remove(file)
            del self._file_and_encrypted[file]

    def view(self, event):
        sel = self._listbox.GetSelection()
        file_name = self._listbox.GetString(sel)
        encrypted_file = os.path.join(
            self._save.dir_name,
            self._file_and_encrypted[file_name],
        )
        c = code_file.CodeFile(encrypted_file, self._save.password)
        msg = get_decrypt_file_data(c)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(
            self,
            msg,
            "%s data" % file_name,
        )
        dlg.ShowModal()

    def edit(self, event):
        sel = self._listbox.GetSelection()
        file_name = self._listbox.GetString(sel)
        frame = Edit(
            None,
            file_name,
            os.path.join(
                self._save.dir_name,
                self._file_and_encrypted[file_name],
            ),
            self._save.password
        )
        frame.Show()

    def rename(self, event):
        sel = self._listbox.GetSelection()
        file = self._listbox.GetString(sel)
        renamed = wx.GetTextFromUser(
            'Rename file %s' % file,
            'Rename',
            file
        ).encode('utf-8')
        if renamed != '':
            if not renamed[-len(FILE_END):] == FILE_END:
                renamed = '%s%s' % (renamed, FILE_END)
            if len(renamed) > LIMIT_CHARACTERS_TO_FILE_NAME:
                wx.MessageBox(
                    "lenght of file name must be under 32 characters",
                    "error",
                    wx.ICON_ERROR
                    )
            else:
                self._listbox.Delete(sel)
                self._listbox.Insert(renamed, sel)
                encrypted = encrypt_file_name(renamed, self._save.password)
                os.rename(
                    os.path.join(
                        self._save.dir_name,
                        self._file_and_encrypted[file],
                    ),
                    os.path.join(
                        self._save.dir_name,
                        encrypted,
                    ),
                )
                index = 0
                for file1 in self._list_items:
                    if file1 == file:
                        break
                    index += 1
                self._list_items[index] = renamed
                del self._file_and_encrypted[file]
                self._file_and_encrypted[renamed] = encrypted

    def new_file(self, event):
        dig = wx.TextEntryDialog(self, 'Enter file name', 'choose name')
        if dig.ShowModal() == wx.ID_OK:
            name = dig.GetValue().encode('utf-8')
            if not name[-len(FILE_END):] == FILE_END:
                name = '%s%s' % (name, FILE_END)
            if self._save.dir_name == name[:len(self._save.dir_name)]:
                path, name = os.path(name)
            name_encrypted = encrypt_file_name(name, self._save.password)
            if name in self._list_items:
                wx.MessageBox("File Exsist!", "error", wx.ICON_ERROR)
            else:
                encrypted = os.path.join(
                    self._save.dir_name,
                    name_encrypted,
                )
                try:
                    open(encrypted, 'w').close()
                    c = code_file.CodeFile(encrypted, self._save.password)
                    with code_file.MyOpen(c, 'w') as cf:
                        cf.write('')
                    if not os.path.exists(encrypted):
                        wx.MessageBox(
                            "sorry, can't make the file, try diffrent name.",
                            "error",
                            wx.ICON_ERROR,
                        )
                        return
                except:
                    wx.MessageBox(
                        "sorry, can't make the file, try diffrent name.",
                        "error",
                        wx.ICON_ERROR
                    )
                    return
            self._listbox.Append(name)
            self._list_items = [name] + self._list_items
            self._file_and_encrypted[name] = name_encrypted

    def OnExit(self, event):
        self.Destroy()


class Edit(wx.Frame):

    def __init__(self, parent, file_name, encrypt_file_full_path, password):
        wx.Frame.__init__(
            self,
            parent,
            title='edit secret file %s' % file_name,
        )
        print 'FILE NAME: %s' % file_name
        self.full_path = encrypt_file_full_path
        self.password = password
        codefile = code_file.CodeFile(
            self.full_path,
            self.password,
        )
        self.text = wx.TextCtrl(
            self,
            -1,
            get_decrypt_file_data(
                codefile
            ),
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
        )
        self.button = wx.Button(self, label="Save")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.text, 1, wx.EXPAND)
        self.sizer.Add(self.button, 0, wx.EXPAND)

        self.SetSizer(self.sizer)
        self.button.Bind(wx.EVT_BUTTON, self.save)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.SetAutoLayout(1)
        self.sizer.Fit(self)
        self.Show(1)
        self.Maximize(True)

    def save(self, event):
        data = self.text.GetValue().encode('utf-8')
        print 'DATA: %s' % data
        codefile = code_file.CodeFile(
            self.full_path,
            self.password,
        )
        print 'FULL PATH: %s' % self.full_path
        with code_file.MyOpen(codefile, 'w') as cf:
            cf.write(data)
        self.Destroy()

    def OnExit(self, event):
        self.Destroy()


def get_decrypt_file_data(codefile):
    text = ''
    with code_file.MyOpen(codefile, 'r') as cf:
        while True:
            tmp = cf.read(BLOCK_SIZE)
            if not tmp:
                break
            text += tmp
    return text


def encrypt_file_name(name, password):

    ''' name - the file (or directory) name.
    password - the password we got to encrypt the name.
    encrypting the name.
    returning the encrypted name.'''

    c = crypte.MyCipher(password, True)

    lenght = c.iv_lenght
    if lenght < 16:
        lenght = '0%s' % str(hex(lenght))[2]
    else:
        lenght = str(hex(lenght))[2:4]
    enc = '%s%s%s' % (lenght, c.iv, c.doFinal(name))

    file_name_encrypt_length = LIMIT_CHARACTERS_TO_FILE_NAME + 12

    if len(enc) < file_name_encrypt_length:
        enc = '%s%s%s' % (
            len(enc),
            enc,
            os.urandom(file_name_encrypt_length - len(enc)),
        )
    return base64.b32encode(enc)


def decrypt_file_name(name, password):

    ''' name - the file (or directory) encrypted name.
    password - the password we got to decrypt the name.
    decrypting the name.
    returning the decrypted name.'''

    e_name = base64.b32decode(name)
    e_name = e_name[2: 2 + int(e_name[:2])]
    len_iv = int(e_name[:2], 16)
    c = crypte.MyCipher(
        password,
        False,
        e_name[2:len_iv + 2]
    )
    return c.doFinal(e_name[len_iv + 2:])


def main():
    saver = Save()
    app = wx.App(False)
    frame = NameAndPassword(None, saver)
    frame.Show()
    app.MainLoop()

    app2 = wx.App(False)
    frame2 = FilesAndOptions(None, saver)
    frame2.Show()
    app2.MainLoop()


if __name__ == '__main__':
    main()
