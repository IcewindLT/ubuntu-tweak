#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import pygtk
pygtk.require("2.0")
import os
import gtk
import gconf

from Config import TweakSettings
from common.LookupIcon import get_icon_with_name
from common.Factory import Factory
from common.Widgets import ListPack, TweakPage, ErrorDialog, QuestionDialog

class Gnome(TweakPage):
    """GNOME Settings"""

    def __init__(self):
        TweakPage.__init__(self)

        self.__setting = TweakSettings()

        notify_hbox = self.create_notify_hbox()
        changeicon_hbox = self.create_change_icon_hbox()

        box = ListPack(_("Panel and Menu"), (
                    Factory.create("gconfcheckbutton", 
                                    _("Confirm Message when removing panel"), 
                                    "confirm_panel_remove"),
                    Factory.create("gconfcheckbutton", 
                                    _("Complete lockdown of the Panel "), 
                                    "locked_down"),
                    Factory.create("gconfcheckbutton", 
                                    _("Enable panel animations"), 
                                    "enable_animations"),
                    Factory.create("gconfcheckbutton", 
                                    _("Show Input Method menu on the Context Menu"), 
                                    "show_input_method_menu"),
                    Factory.create("gconfcheckbutton",
                                    _("Show Unicode Method menu on the Context Menu"), 
                                    "show_unicode_menu"),
                    changeicon_hbox,
                    notify_hbox,
            ))
        self.pack_start(box, False, False, 0)

        box = ListPack(_("Screensaver"), (
                    Factory.create("gconfcheckbutton", _("Enable User Switching when Screen is locked."), "user_switch_enabled"),
            ))
        self.pack_start(box, False, False, 0)

        self.recently_used = gtk.CheckButton(_("Enable System-wide 'Recently Used' list"))
        self.recently_used.connect('toggled', self.colleague_changed)
        self.recently_used.set_active(self.get_state())
        box = ListPack(_("History"), (
                    self.recently_used,
            ))
        self.pack_start(box, False, False, 0)

    def create_notify_hbox(self):
        hbox = gtk.HBox(False, 10)
        label = gtk.Label(_("Notification-daemon popup location"))
        label.set_alignment(0, 0.5)
        combobox = Factory.create("gconfcombobox", 
                                  "popup_location", 
                                  [_("Top Left"), _("Top Right"), _("Bottom Left"), _("Bottom Right")], 
                                  ["top_left", "top_right", "bottom_left", "bottom_right"])
        hbox.pack_start(label, False, False, 0)
        hbox.pack_start(combobox)

        return hbox

    def create_change_icon_hbox(self):
        hbox = gtk.HBox(False, 10)
        label = gtk.Label(_('Click the button to change panel logo'))
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 0)

        button = gtk.Button()
        button.connect('clicked', self.on_change_icon_clicked)
        image = gtk.image_new_from_pixbuf(get_icon_with_name('start-here', 24))
        button.set_image(image)
        hbox.pack_end(button, False, False, 0)

        return hbox

    def on_change_icon_clicked(self, widget):
        dialog = gtk.FileChooserDialog(_('Choose a new logo'),action = gtk.FILE_CHOOSER_ACTION_OPEN, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name(_("PNG image (*.png)"))
        filter.add_mime_type("image/png")
        dialog.set_current_folder(os.path.expanduser('~'))
        dialog.add_filter(filter)

        filename = ''
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()

        dialog.destroy()

        if filename:
            pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
            w, h = pixbuf.get_width(), pixbuf.get_height()
            if w != 24 or h != 24:
                ErrorDialog(_("The size isn't suitable for the panel.\nIt should be 24x24.")).launch()
            else:
                dest = os.path.expanduser('~/.icons/%s/24x24/places/start-here.png' % self.__setting.get_icon_theme())
                os.system('mkdir -p %s' % os.path.dirname(dest))
                os.system('cp %s %s' % (filename, dest))

                image = gtk.image_new_from_file(dest)
                widget.set_image(image)

                dialog = QuestionDialog(_('Do you want take effect immediately?'))
                if dialog.run() == gtk.RESPONSE_YES:
                    os.system('killall gnome-panel')

                dialog.destroy()

    def get_state(self):
        file = os.path.join(os.path.expanduser("~"), ".recently-used.xbel")
        if os.path.exists(file):
            if os.path.isdir(file):
                return False
            elif os.path.isfile(file):
                return True
        else:
            return True

    def colleague_changed(self, widget):
        enabled = self.recently_used.get_active()
        file = os.path.expanduser("~/.recently-used.xbel")
        if enabled:
            os.system('rm -r %s' % file)
            os.system('touch %s' % file)
        else:
            os.system('rm -r %s' % file)
            os.system('mkdir %s' % file)

if __name__ == "__main__":
    from Utility import Test
    Test(Gnome)
