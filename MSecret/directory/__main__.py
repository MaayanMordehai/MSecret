#
## @package MSecret.__main__
## @file __main__.py Implementation of @ref MSecret.__main__
#


import base64
import os
import wx
import wx.lib.dialogs

from ..common import delete
from ..common import crypte
from ..common import code_file
from ..common import save


## BLOCK_SIZE for read and write to\from file
BLOCK_SIZE = 1024
## only legal file end
FILE_END = '.txt'
## LIMIT_CHARACTERS on encrypt file name
LIMIT_CHARACTERS = 60
## encryption
ENC = 'MSecret'
## optional ENCRYPTIONS
ENCRYPTIONS = ['AES', 'MSecret']


## user interface object
#
# Frame to get information
#
class NameAndPassword(wx.Frame):

    ## Constructor
    def __init__(self, parent, save):
        self._save = save

        wx.Frame.__init__(
            self,
            parent,
            title='Enter Directory And Password',
        )

        panel = wx.Panel(self)

        button = wx.Button(
            panel,
            label='create new directory',
        )

        button2 = wx.Button(
            panel,
            label='read or edit directory',
        )

        lblfile = wx.StaticText(
            panel,
            label="directory:",
        )
        self._editfile = wx.TextCtrl(
            panel,
            size=(140, -1),
        )

        lblpassword = wx.StaticText(
            panel,
            label="password:",
        )
        self._editpassword = wx.TextCtrl(
            panel,
            style=wx.TE_PASSWORD,
            size=(140, -1),
        )

        self._rbox = wx.RadioBox(
            panel,
            label='encryption',
            choices=ENCRYPTIONS,
            majorDimension=1,
            style=wx.RA_SPECIFY_ROWS
        )

        # Set sizer for the frame, so we can change frame size to match widgets
        windowSizer = wx.BoxSizer()
        windowSizer.Add(
            panel,
            1,
            wx.ALL | wx.EXPAND,
        )

        # Set sizer for the panel content)
        sizer = wx.GridBagSizer(6, 6)
        sizer.Add(
            lblfile,
            (0, 0),
        )
        sizer.Add(
            self._editfile,
            (0, 1),
        )
        sizer.Add(
            lblpassword,
            (1, 0),
        )
        sizer.Add(
            self._editpassword,
            (1, 1),
        )
        sizer.Add(
            button2,
            (2, 0),
            flag=wx.EXPAND,
        )
        sizer.Add(
            button,
            (2, 1),
            flag=wx.EXPAND,
        )
        sizer.Add(
            self._rbox,
            (3, 0),
            flag=wx.EXPAND,
        )

        border = wx.BoxSizer()

        border.Add(
            sizer,
            1,
            wx.ALL | wx.EXPAND,
            5,
        )

        # Use the sizers
        panel.SetSizerAndFit(border)
        self.SetSizerAndFit(windowSizer)

        # Set event handlers
        button2.Bind(
            wx.EVT_BUTTON,
            self.edit_dir_button,
        )
        button.Bind(
            wx.EVT_BUTTON,
            self.create_dir_button,
        )
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self._rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

    ## saving radio box information
    # @param e (event) event
    #
    # only if radio box was pressed
    #
    def onRadioBox(self, e):
        self._save.encryption = ENCRYPTIONS[self._rbox.GetSelection()]

    ## saving password and dir name
    # @param e (event) event
    #
    # only if edit dir button was pressed
    #
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

    ## saving password and dir name, create dir
    # @param e (event) event
    #
    # only if create dir button was pressed
    #
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

    ## exit nicely
    # @param event (event) event
    #
    # only if x was pressed
    #
    def OnExit(self, event):
        self._save.should_exit = True
        self.Destroy()


## user interface object
#
# Frame for user access
#
class FilesAndOptions(wx.Frame):

    ## Constructor
    def __init__(self, parent, save):

        if save.encryption is None:
            save.encryption = ENCRYPTIONS[0]
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

    ## delete file
    # @param event (event) event
    #
    # only if delete button pressed
    #
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

    ## view file
    # @param event (event) event
    #
    # only if view button pressed
    #
    def view(self, event):
        sel = self._listbox.GetSelection()
        file_name = self._listbox.GetString(sel)
        encrypted_file = os.path.join(
            self._save.dir_name,
            self._file_and_encrypted[file_name],
        )
        print encrypted_file
        c = code_file.CodeFile(encrypted_file, self._save.password)
        msg = get_decrypt_file_data(c)
        dlg = wx.lib.dialogs.ScrolledMessageDialog(
            self,
            msg,
            "%s data" % file_name,
        )
        dlg.ShowModal()

    ## edit file
    # @param event (event) event
    #
    # only if edit button pressed
    #
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
            self._save.password,
            self._save.encryption,
        )
        frame.Show()

    ## rename file
    # @param event (event) event
    #
    # only if rename button pressed
    #
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
            encrypted = encrypt_file_name(
                renamed,
                self._save.password,
                self._save.encryption,
            )
            self._listbox.Delete(sel)
            self._listbox.Insert(renamed, sel)
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

    ## create new file
    # @param event (event) event
    #
    # only if new file button pressed
    #
    def new_file(self, event):
        dig = wx.TextEntryDialog(self, 'Enter file name', 'choose name')
        if dig.ShowModal() == wx.ID_OK:
            name = dig.GetValue().encode('utf-8')
            if not name[-len(FILE_END):] == FILE_END:
                name = '%s%s' % (name, FILE_END)
            name_encrypted = encrypt_file_name(
                name,
                self._save.password,
                self._save.encryption,
            )
            if name in self._list_items:
                wx.MessageBox("File Exsist!", "error", wx.ICON_ERROR)
            else:
                encrypted = os.path.join(
                    self._save.dir_name,
                    name_encrypted,
                )
                try:
                    open(encrypted, 'w').close()
                    c = code_file.CodeFile(
                        encrypted,
                        self._save.password,
                        self._save.encryption,
                    )
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
                    raise

            self._listbox.Append(name)
            self._list_items = [name] + self._list_items
            self._file_and_encrypted[name] = name_encrypted

    ## exit nicely
    # @param event (event) event
    #
    # only if x was pressed
    #
    def OnExit(self, event):
        self.Destroy()


class Edit(wx.Frame):

    ## Constructor
    def __init__(
        self,
        parent,
        file_name,
        encrypt_file_full_path,
        password,
        enc,
    ):
        wx.Frame.__init__(
            self,
            parent,
            title='edit secret file %s' % file_name,
        )
        self._encryption = enc
        self._full_path = encrypt_file_full_path
        self._password = password
        codefile = code_file.CodeFile(
            self._full_path,
            self._password,
        )
        self.text = wx.TextCtrl(
            self,
            -1,
            get_decrypt_file_data(
                codefile
            ),
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER,
        )
        button = wx.Button(self, label="Save")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text, 1, wx.EXPAND)
        sizer.Add(button, 0, wx.EXPAND)

        self.SetSizer(sizer)
        button.Bind(wx.EVT_BUTTON, self.save)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.SetAutoLayout(1)
        sizer.Fit(self)
        self.Show(1)
        self.Maximize(True)

    ## save to code file
    # @param event (event) event
    #
    # only if view button pressed
    #
    def save(self, event):
        data = self.text.GetValue().encode('utf-8')
        print 'data: %s' % data
        codefile = code_file.CodeFile(
            self._full_path,
            self._password,
            self._encryption,
        )
        with code_file.MyOpen(codefile, 'w') as cf:
            cf.write(data)
        self.Destroy()

    ## exit nicely
    # @param event (event) event
    #
    # only if x was pressed
    #
    def OnExit(self, event):
        self.Destroy()


## get code file content
# @param codefile CodeFile
#
def get_decrypt_file_data(codefile):
    text = ''
    with code_file.MyOpen(codefile, 'r') as cf:
        while True:
            tmp = cf.read(BLOCK_SIZE)
            if not tmp:
                break
            text += tmp
    return text


## encrypt file name
# @param name (str) file name
# @param password (str) password
#
def encrypt_file_name(name, password, encr):

    ''' name - the file (or directory) name.
    password - the password we got to encrypt the name.
    encrypting the name.
    returning the encrypted name.'''

    if encr == ENCRYPTIONS[1]:
        c = crypte.MyCipher(password, True)
    elif encr == ENCRYPTIONS[0]:
        c = crypte.AesCipher(password, True)
    enc_len = len(encr)
    if enc_len < 16:
        enc_len = '0%s' % str(hex(enc_len))[2]
    else:
        enc_len = str(hex(enc_len))[2:4]
    lenght = c.iv_lenght
    if lenght < 16:
        lenght = '0%s' % str(hex(lenght))[2]
    else:
        lenght = str(hex(lenght))[2:4]
    encrypted = '%s%s%s%s%s' % (enc_len, encr, lenght, c.iv, c.doFinal(name))
    encrypted = '%s%s' % (len(encrypted), encrypted)
    if len(encrypted) < LIMIT_CHARACTERS:
        encrypted = '%s%s' % (
            encrypted,
            os.urandom(LIMIT_CHARACTERS - len(encrypted)),
        )
    else:
        wx.MessageBox(
            "sorry, can't make the file, name too long.",
            "error",
            wx.ICON_ERROR
        )
    return base64.b32encode(encrypted)

## decrypt file name
# @param name (str) encrypted file name
# @param password (str) password
#
def decrypt_file_name(name, password):

    ''' name - the file (or directory) encrypted name.
    password - the password we got to decrypt the name.
    decrypting the name.
    returning the decrypted name.'''

    e_name = base64.b32decode(name)
    e_name = e_name[2: 2 + int(e_name[:2])]
    len_encry = int(e_name[:2], 16)
    encryption = e_name[2:len_encry + 2]
    e_name = e_name[len_encry + 2:]
    len_iv = int(e_name[:2], 16)
    if encryption == ENCRYPTIONS[0]:
        c = crypte.AesCipher(
            password,
            False,
            e_name[2:len_iv + 2],
        )
    elif encryption == ENCRYPTIONS[1]:
        c = crypte.MyCipher(
            password,
            False,
            e_name[2:len_iv + 2]
        )
    return c.doFinal(e_name[len_iv + 2:])


## Main implementation
def main():
    saver = save.Save()
    app = wx.App(False)
    frame = NameAndPassword(None, saver)
    frame.Show()
    app.MainLoop()
    if not saver.should_exit:
        app2 = wx.App(False)
        frame2 = FilesAndOptions(None, saver)
        frame2.Show()
        app2.MainLoop()


if __name__ == '__main__':
    main()
