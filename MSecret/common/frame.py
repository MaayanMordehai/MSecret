#
## @package MSecret.frame user interface module.
## @file frame.py Implementation of @ref MSecret.frame
#


import wx
import os
from save import Save

## optional encryptions
ENCRYPTIONS = ['AES', 'MSecret']
## dict for making button response boolean
YES_NO = {'yes': True, 'no': False}


## user interface object
#
# Frame to get information
#
class FrameForPassword(wx.Frame):

    ## Constructor
    def __init__(self, parent, save, file_name, encry, dir):
        self._save = save

        wx.Frame.__init__(
            self,
            parent,
            title='password '
        )

        panel = wx.Panel(self)

        problem = wx.StaticText(
            panel,
            label=" for file %s" % file_name,
        )
        problem.SetForegroundColour(wx.BLUE)

        label = 'done'
        button = wx.Button(
            panel,
            label=label,
        )
        lblpassword = wx.StaticText(
            panel,
            label="Your password:",
        )
        self._editpassword = wx.TextCtrl(
            panel,
            style=wx.TE_PASSWORD,
            size=(140, -1),
        )

        if encry:
            self._rbox0 = wx.RadioBox(
                panel,
                label='encryption',
                choices=ENCRYPTIONS,
                majorDimension=1,
                style=wx.RA_SPECIFY_ROWS
            )
        if dir:
            self._rbox1 = wx.RadioBox(
                panel,
                label='recursive?',
                choices=sorted(YES_NO.keys()),
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
            lblpassword,
            (1, 0),
        )
        sizer.Add(
            self._editpassword,
            (1, 1),
        )
        sizer.Add(
            button,
            (2, 1),
            flag=wx.EXPAND,
        )
        sizer.Add(
            problem,
            (0, 0),
        )
        if encry:
            sizer.Add(
                self._rbox0,
                (2, 0),
                flag=wx.EXPAND,
            )
        if dir:
            sizer.Add(
                self._rbox1,
                (3, 0),
                flag=wx.EXPAND,
            )

        # Set simple sizer for a nice border
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
        button.Bind(
            wx.EVT_BUTTON,
            self.button_result,
        )
        if encry:
            self._rbox0.Bind(wx.EVT_RADIOBOX, self.radio0)
        if dir:
            self._rbox1.Bind(wx.EVT_RADIOBOX, self.radio1)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

    ## saving radio box 1 information
    # @param e (event) event
    #
    # only if radio box 1 was prssed
    #
    def radio1(self, e):
        self._save.recursive = sorted(
            YES_NO.keys()
        )[self._rbox1.GetSelection()]

    ## saving radio box 0 information
    # @param e (event) event
    #
    # only if radio box 0 was prssed
    #
    def radio0(self, e):
        self._save.encryption = ENCRYPTIONS[self._rbox0.GetSelection()]

    ## saving password
    # @param e (event) event
    #
    # only if button was prssed
    #
    def button_result(self, e):
        self._save.password = self._editpassword.GetValue()
        self.Destroy()

    ## exit nicely
    # @param e (event) event
    #
    # only if x was prssed
    #
    def OnExit(self, event):
        self._save.should_exit = True
        self.Destroy()

## showing the frame
# @param file_name (string) file name's frame
# @returns information from frame
#
def Show_Frame(file_name, enc):
    ''' showing frame and returning file name and password
    that the user wrote '''
    s = Save()
    app = wx.App(False)
    dir = os.path.isdir(file_name)
    frame = FrameForPassword(None, s, file_name, enc, dir)
    frame.Show()
    app.MainLoop()
    return s.password, s.encryption, s.recursive, s.should_exit
