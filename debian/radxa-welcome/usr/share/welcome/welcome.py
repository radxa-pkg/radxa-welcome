#! /usr/bin/python3
#
# Copyright 2024 Radxa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gettext
import welcome_support
from welcome_support import (
    _,
    settings,
    lp,
)
from locale import getlocale
from webbrowser import open
from os import path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk


class WelcomeApp(Adw.Application):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app) -> None:
        self.create_action("about", self.on_about_action)

    def do_activate(self) -> None:
        """Callback for the app.activate signal."""

        global win
        win = self.props.active_window
        if not win:
            win = WelcomeWindow(application=self)
            self.win = win
        win.present()

    def on_preferences_action(self, widget, _) -> None:
        """Callback for the app.preferences action."""
        pass

    def on_about_action(self, widget, py) -> None:
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Radxa Welcome",
            application_icon="com.radxa.welcome-text",
            developer_name="Radxa",
            version="0.0.1",
            developers=["Panda"],
            copyright="© 2024 Radxa",
            license_type=Gtk.License.GPL_3_0,
            website="https://radxa.com",
        )
        about.add_acknowledgement_section(_("Special thanks to"), ["Shivanandvp"])
        about.present()

    def create_action(self, name, callback, shortcuts=None) -> None:
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


@Gtk.Template(resource_path="/com/radxa/welcome/ui/window.ui")
class WelcomeWindow(Adw.Window):
    __gtype_name__ = "WelcomeWindow"

    header_bar: Gtk.HeaderBar = Gtk.Template.Child()
    stack: Adw.ViewStack = Gtk.Template.Child()
    autolaunch: Gtk.CheckButton = Gtk.Template.Child()
    close_button: Gtk.Button = Gtk.Template.Child()

    home_page: Adw.ViewStackPage = Gtk.Template.Child()
    website_button: Gtk.Button = Gtk.Template.Child()
    forums_button: Gtk.Button = Gtk.Template.Child()
    docs_button: Gtk.Button = Gtk.Template.Child()
    discord_button: Gtk.Button = Gtk.Template.Child()
    wechat_popover: Gtk.Popover = Gtk.Template.Child()
    wechat_qr: Gtk.Image = Gtk.Template.Child()
    qq_popover: Gtk.Popover = Gtk.Template.Child()
    qq_qr: Gtk.Image = Gtk.Template.Child()
    qq_icon: Gtk.Image = Gtk.Template.Child()
    discord_icon: Gtk.Image = Gtk.Template.Child()
    wechat_icon: Gtk.Image = Gtk.Template.Child()

    config_page: Adw.ViewStackPage = Gtk.Template.Child()
    about_page: Adw.ViewStackPage = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Connect buttons
        self.website_button.connect("clicked", self.on_button_clicked)
        self.forums_button.connect("clicked", self.on_button_clicked)
        self.docs_button.connect("clicked", self.on_button_clicked)
        self.discord_button.connect("clicked", self.on_discord_button_clicked)
        self.wechat_qr.set_from_file(
            path.join(path.dirname(__file__), "data/assets/wechat-qr-dark.svg")
        )
        self.wechat_icon.set_from_file(
            path.join(path.dirname(__file__), "data/assets/wechat-icon.svg")
        )
        self.qq_icon.set_from_file(
            path.join(path.dirname(__file__), "data/assets/qq-icon.svg")
        )
        self.qq_qr.set_from_file(
            path.join(path.dirname(__file__), "data/assets/qq-qr-dark.svg")
        )
        self.discord_icon.set_from_file(
            path.join(path.dirname(__file__), "data/assets/discord-icon.svg")
        )

    def on_button_clicked(self, button) -> None:
        try:
            button_name = button.get_child().get_label()
        except AttributeError:
            button_name = button.get_child().get_children()[1].get_label()
        if button_name == _("Website"):
            open("https://radxa.com/", new=2)
        elif button_name == _("Forums"):
            open("https://forum.radxa.com/", new=2)
        elif button_name == _("Documentation"):
            if getlocale()[0] == "zh_CN":
                open("https://docs.radxa.com/", new=2)
            else:
                open("https://docs.radxa.com/en/", new=2)

    def on_discord_button_clicked(self, button) -> None:
        open("https://rock.sh/go", new=2)
