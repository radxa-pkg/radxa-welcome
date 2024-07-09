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
import subprocess
import welcome_support
from welcome_support import (
    _,
    p_,
    app_settings,
    apps,
    lp,
    change_autolaunch,
    lrun,
    debounce,
    add_custom_styling,
    load_css,
    settings_get,
    settings_set,
    check_installed,
)
from locale import getlocale
from webbrowser import open
from os import path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib  # type: ignore


class WelcomeApp(Adw.Application):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.connect("activate", self.on_activate)
        global css_provider
        css_provider = load_css(path.dirname(__file__) + "/data/ui/main.css")

    def on_activate(self, app) -> None:
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)

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
        preferences: Adw.PreferencesWindow = Preferences()
        preferences.present()

    def on_about_action(self, widget, py) -> None:
        """Callback for the app.about action."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Radxa Welcome",
            application_icon="com.radxa.welcome-text",
            developer_name="Radxa",
            version="0.0.1",
            developers=["Panda"],
            copyright="© 2024 Radxa Computer Co., Ltd",
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


@Gtk.Template(resource_path="/com/radxa/welcome/ui/preferences.ui")
class Preferences(Adw.PreferencesWindow):
    __gtype_name__ = "preferences_window"

    autolaunch: Gtk.Switch = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # set autolaunch to the value in settings
        self.autolaunch.set_active(settings_get("autostart", True))
        self.autolaunch.connect("state-set", self.on_autolaunch_toggled)

    def on_autolaunch_toggled(self, button, *_) -> None:
        change_autolaunch(button.get_active())


@Gtk.Template(resource_path="/com/radxa/welcome/ui/window.ui")
class WelcomeWindow(Adw.Window):
    __gtype_name__ = "WelcomeWindow"

    header_bar: Gtk.HeaderBar = Gtk.Template.Child()
    stack: Gtk.Stack = Gtk.Template.Child()
    carousel: Adw.Carousel = Gtk.Template.Child()
    carousel_indicator: Adw.CarouselIndicatorDots = Gtk.Template.Child()

    welcome_button: Gtk.Button = Gtk.Template.Child()
    next_button: Gtk.Button = Gtk.Template.Child()
    previous_button: Gtk.Button = Gtk.Template.Child()

    autolaunch: Gtk.Switch = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        add_custom_styling(self, css_provider)

        if settings_get("fist_run", True):
            self.stack.set_visible_child_name("welcome_page")
            self.header_bar.set_visible(False)
            self.carousel_indicator.set_visible(False)
        else:
            self.stack.set_visible_child_name("content_page")

        # Carousel setup
        self.links_page = LinksPage(window=self)
        self.apps_page = AppsPage(window=self)
        self.pages: list = [self.links_page, self.apps_page]

        self.carousel.append(self.links_page)
        self.carousel.append(self.apps_page)
        self.carousel.connect("page-changed", self.update_buttons)

        # Auto launch switch
        self.autolaunch.set_active(settings_get("autostart", True))
        self.autolaunch.connect("state-set", self.on_autolaunch_toggled)

        # Connect buttons
        self.welcome_button.connect("clicked", self.on_welcome_button_clicked)
        self.next_button.connect("clicked", self.on_next_button_clicked)
        self.previous_button.connect("clicked", self.on_previous_button_clicked)

        style_manager = Adw.StyleManager.get_default()
        style_manager.set_property("color-scheme", Adw.ColorScheme.FORCE_DARK)
        self.update_buttons()

    def update_buttons(self, *_) -> None:
        num_pages: int = self.carousel.get_n_pages()
        curr_page: int = int(self.carousel.get_position())
        lp(curr_page, mode="debug")
        lp(num_pages, mode="debug")
        self.previous_button.set_visible(curr_page > 0)
        self.next_button.set_visible(curr_page < num_pages - 1)

    @debounce(0.5)
    def on_next_button_clicked(self, button) -> None:
        curr_page: int = int(self.carousel.get_position())
        self.carousel.scroll_to(self.pages[curr_page + 1], True)
        self.update_buttons()

    @debounce(0.5)
    def on_previous_button_clicked(self, button) -> None:
        curr_page: int = int(self.carousel.get_position())
        self.carousel.scroll_to(self.pages[curr_page - 1], True)
        self.update_buttons()

    def on_welcome_button_clicked(self, button, *_) -> None:
        self.stack.set_visible_child_name("content_page")
        self.header_bar.set_visible(True)
        self.carousel_indicator.set_visible(True)
        change_autolaunch(self.autolaunch.get_active())
        settings_set("fist_run", False)

    def on_autolaunch_toggled(self, button, *_) -> None:
        change_autolaunch(button.get_active())


@Gtk.Template(resource_path="/com/radxa/welcome/ui/links_page.ui")
class LinksPage(Adw.Bin):
    __gtype_name__ = "links_page"

    website_button: Gtk.Button = Gtk.Template.Child()
    forums_button: Gtk.Button = Gtk.Template.Child()
    docs_button: Gtk.Button = Gtk.Template.Child()
    discord_button: Gtk.Button = Gtk.Template.Child()
    wechat_qr: Gtk.Image = Gtk.Template.Child()
    wechat_icon: Gtk.Image = Gtk.Template.Child()
    qq_icon: Gtk.Image = Gtk.Template.Child()
    qq_qr: Gtk.Image = Gtk.Template.Child()
    discord_icon: Gtk.Image = Gtk.Template.Child()
    discourse_icon: Gtk.Image = Gtk.Template.Child()

    def __init__(self, window, **kwargs) -> None:
        super().__init__(**kwargs)
        self.window = window
        # Connect buttons
        self.website_button.connect("clicked", self.on_website_button_clicked)
        self.forums_button.connect("clicked", self.on_forums_button_clicked)
        self.docs_button.connect("clicked", self.on_docs_button_clicked)
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
        self.discourse_icon.set_from_file(
            path.join(path.dirname(__file__), "data/assets/discourse-icon.svg")
        )

    def on_discord_button_clicked(self, button) -> None:
        open("https://rock.sh/go", new=2)

    def on_website_button_clicked(self, button) -> None:
        open("https://radxa.com/", new=2)

    def on_forums_button_clicked(self, button) -> None:
        open("https://forum.radxa.com/", new=2)

    def on_docs_button_clicked(self, button) -> None:
        if getlocale()[0] == "zh_CN":
            open("https://docs.radxa.com/", new=2)
        else:
            open("https://docs.radxa.com/en/", new=2)


@Gtk.Template(resource_path="/com/radxa/welcome/ui/apps_page.ui")
class AppsPage(Adw.Bin):
    __gtype_name__ = "apps_page"

    rsetup_button: Gtk.Button = Gtk.Template.Child()
    software_button: Gtk.Button = Gtk.Template.Child()
    terminal_button: Gtk.Button = Gtk.Template.Child()
    task_manager_button: Gtk.Button = Gtk.Template.Child()
    settings_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, window, **kwargs) -> None:
        super().__init__(**kwargs)
        self.window: Adw.Window = window

        self.rsetup_button.connect("clicked", self.on_rsetup_button_clicked)
        self.software_button.connect("clicked", self.on_software_button_clicked)
        self.terminal_button.connect("clicked", self.on_terminal_button_clicked)
        self.task_manager_button.connect("clicked", self.on_task_manager_button_clicked)
        self.settings_button.connect("clicked", self.on_settings_button_clicked)

    def on_rsetup_button_clicked(self, button) -> None:
        lrun(["gtk-launch", "rsetup"], wait=False)

    def on_software_button_clicked(self, button) -> None:
        check_installed("software_center", window=self.window)

    def on_terminal_button_clicked(self, button) -> None:
        check_installed("terminal", window=self.window)

    def on_task_manager_button_clicked(self, button) -> None:
        check_installed("task_manager", window=self.window)

    def on_settings_button_clicked(self, button) -> None:
        check_installed("settings", window=self.window)
