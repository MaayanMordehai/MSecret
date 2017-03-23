
import os
import wx


class FrameForPassword(wx.Frame):
    '''
    class FrameForPassword to make a window where
    user will write what is the password
    '''

    def __init__(self, parent, save, file_name):
        self._save = save

        wx.Frame.__init__(
            self,
            parent,
            title='set password '
        )

        self._panel = wx.Panel(self)

        self._problom = wx.StaticText(
            self._panel,
            label=" for file %s" % file_name,
        )
        self._problom.SetForegroundColour(wx.BLUE)

        label = 'done'
        self._problom = wx.StaticText(
            self._panel,
            label=""
        )
        self._problom.SetForegroundColour(wx.RED)

        self._button = wx.Button(
            self._panel,
            label=label,
        )
        self._lblpassword = wx.StaticText(
            self._panel,
            label="Your password:",
        )
        self._editpassword = wx.TextCtrl(
            self._panel,
            style=wx.TE_PASSWORD,
            size=(140, -1),
        )
        self._password = ""
        self._file = ""

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
            self._lblpassword,
            (1, 0),
        )
        self._sizer.Add(
            self._editpassword,
            (1, 1),
        )
        self._sizer.Add(
            self._button,
            (2, 1),
            flag=wx.EXPAND,
        )
        self._sizer.Add(
            self._problom,
            (0, 0),
        )

        # Set simple sizer for a nice border
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
        self._button.Bind(
            wx.EVT_BUTTON,
            self.button_result,
        )

    def button_result(self, e):
        self._save.set_password(self._editpassword.GetValue())
        self.Destroy()


class Save(object):
    def __init__(self):
        self._file = ''
        self._password = ''
        self._del = False
        self._encrypt = None

    def get_password(self):
        return self._password

    def set_password(self, password):
        self._password = password



class Frame(wx.Frame):
    '''class Frame to make a window where
    the user will write what is the file
    name and what is the password 
    '''

    def __init__(self, parent, save):
        self._save = save
        if self._save.get_encrypt():
            title = 'encrypt'
        else:
            title = 'decrypt'
        wx.Frame.__init__(
            self,
            parent,
            title=title
        )

        self._del = False

        self._panel = wx.Panel(self)
        self._lblfile = wx.StaticText(
            self._panel,
            label="Your file:",
        )
        self._editfile = wx.TextCtrl(
            self._panel,
            size=(140, -1),
        )
        if self._save.get_encrypt():
            self._delete_button = wx.Button(
                self._panel,
                label="delete original file",
            )
            label = 'Encrypte'
        else:
            label = 'Decrypte'
            self._problom = wx.StaticText(
                self._panel,
                label=""
            )
            self._problom.SetForegroundColour(wx.RED)

        self._button = wx.Button(
            self._panel,
            label=label,
        )
        self._lblpassword = wx.StaticText(
            self._panel,
            label="Your password:",
        )
        self._editpassword = wx.TextCtrl(
            self._panel,
            style=wx.TE_PASSWORD,
            size=(140, -1),
        )
        self._password = ""
        self._file = ""

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
            self._button,
            (2, 0),
            flag=wx.EXPAND,
        )
        if self._save.get_encrypt():
            self._sizer.Add(
                self._delete_button,
                (2, 1),
                flag=wx.EXPAND,
            )
        else:
            self._sizer.Add(
                self._problom,
                (2, 1),
            )

        # Set simple sizer for a nice border
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
        self._button.Bind(
            wx.EVT_BUTTON,
            self.button_result,
        )
        if self._save.get_encrypt():
            self._delete_button.Bind(
                wx.EVT_BUTTON,
                self.button_delete,
            )

    def button_result(self, e):
        self._save.set_file(self._editfile.GetValue())
        self._save.set_password(self._editpassword.GetValue())
        self._save.set_del(self._del)
        if not self._save.get_encrypt():
            if self._save.get_file()[- len('.encrypted'):] != '.encrypted':
                self._problom.SetLabel("file need to end with '.encrypted'")
            else:
                self.Destroy()
        else:
            self.Destroy()

    def button_delete(self, e):
        self._del = True


class Save2(object):
    def __init__(self):
        self._file = ''
        self._password = ''
        self._del = False
        self._encrypt = None

    def set_encrypt(self, encrypt):
        self._encrypt = encrypt

    def get_encrypt(self):
        return self._encrypt

    def get_del(self):
        return self._del

    def get_file(self):
        return self._file

    def get_password(self):
        return self._password

    def set_del(self, delete):
        self._del = delete

    def set_file(self, file):
        self._file = file

    def set_password(self, password):
        self._password = password


def Show_Frame(file_name):
    ''' showing frame and returning file name and password
    that the user wrote '''
    s = Save()
    app = wx.App(False)
    frame = FrameForPassword(None, s, file_name)
    frame.Show()
    app.MainLoop()
    print s.get_password()
    return s.get_password().encode('utf8')
