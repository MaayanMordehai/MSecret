
import wx
import os


ENCRYPTIONS = ['AES', 'MSecret']
YES_NO = {'yes': True, 'no': False}


class FrameForPassword(wx.Frame):
    '''
    class FrameForPassword to make a window where
    user will write what is the password
    '''

    def __init__(self, parent, save, file_name, encry, dir):
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

        if encry:
            self._rbox0 = wx.RadioBox(
                self._panel,
                label = 'encryption',
                choices = ENCRYPTIONS,
                majorDimension = 1,
                style = wx.RA_SPECIFY_ROWS
            )
        if dir:
            self._rbox1 = wx.RadioBox(
                self._panel,
                label = 'recursive?',
                choices = sorted(YES_NO.keys()),
                majorDimension = 1,
                style = wx.RA_SPECIFY_ROWS
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
        if encry:
            self._sizer.Add(
                self._rbox0,
                (2, 0),
                flag=wx.EXPAND,
            )
        if dir:
            self._sizer.Add(
                self._rbox1,
                (3, 0),
                flag=wx.EXPAND,
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
        if encry:
            self._rbox0.Bind(wx.EVT_RADIOBOX, self.radio0)
        if dir:
            self._rbox1.Bind(wx.EVT_RADIOBOX, self.radio1)

    def radio1(self, e):
        self._save.recursive = sorted(YES_NO.keys())[self._rbox1.GetSelection()]

    def radio0(self, e):
        self._save.encryption = ENCRYPTIONS[self._rbox0.GetSelection()]

    def button_result(self, e):
        self._save.password = self._editpassword.GetValue()
        self.Destroy()


class Save(object):
    def __init__(self):
        self._password = ''
        self._enc = ''
        self._recursive = None

    @property
    def recursive(self):
        return self._recursive

    @recursive.setter
    def recursive(self, re):
        self._recursive = re

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def encryption(self):
        return self._enc

    @encryption.setter
    def encryption(self, e):
        self._enc = e


def Show_Frame(file_name, enc):
    ''' showing frame and returning file name and password
    that the user wrote '''
    s = Save()
    app = wx.App(False)
    dir = os.path.isdir(file_name)
    frame = FrameForPassword(None, s, file_name, enc, dir)
    frame.Show()
    app.MainLoop()
    return s.password, s.encryption, s.recursive

