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
import logging
import os
from os import path
import subprocess
from time import sleep, monotonic
from pathlib import Path
from threading import Lock
from functools import wraps
from traceback import print_exception
from datetime import datetime
from typing import Any
from pyrunning import LoggingHandler, Command, LogMessage
from pysetting import JSONConfiguration

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib  # type: ignore


def setup_translations(lang: object = None) -> gettext.GNUTranslations:
    """
    Setup translations

        Does the following:
        - Loads the translations from the locale folder
        - Sets the translations for the gettext module

        Returns:  A gettext translation object and a pgettext translation object
        :rtype: object
    """
    lang_path = path.join(path.dirname(__file__), "locale")
    # Load translations
    if lang is not None:
        print("Loading translations for", lang)
        gettext.bindtextdomain("welcome", lang_path)
        gettext.textdomain("welcome")
        translation = gettext.translation("welcome", lang_path, languages=[lang])
        translation.install()
        return translation.gettext  # type: ignore
    else:
        gettext.bindtextdomain("welcome", lang_path)
        gettext.textdomain("welcome")
        return gettext.gettext, gettext.pgettext  # type: ignore


def setup_logging() -> logging.Logger:
    """
    Setup logging

        Does the following:
        - Creates a logger with a name
        - Sets the format for the logs
        - Sets up logging to a file and future console
    """

    logger = logging.getLogger("radxa-welcome")
    logger.setLevel(logging.DEBUG)

    log_dir = os.path.join(os.path.expanduser("~"), ".cache", "welcome", "logs")
    log_file = os.path.join(
        log_dir, datetime.now().strftime("radxa-welcome-%Y-%m-%d-%H-%M-%S.log")
    )
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        if not os.path.isdir(log_dir):
            raise FileNotFoundError("The directory {} does not exist".format(log_dir))
        # get write perms
        elif not os.access(log_dir, os.W_OK):
            raise PermissionError(
                "You do not have permission to write to {}".format(log_dir)
            )
    except Exception as e:
        print_exception(type(e), e, e.__traceback__)
        exit(1)

    print("Logging to:", log_file)

    log_file_handler = logging.FileHandler(log_file)
    log_file_handler.setLevel(logging.DEBUG)
    log_file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)8s] %(message)s",
    )
    log_file_handler.setFormatter(log_file_formatter)
    logger.addHandler(log_file_handler)

    log_error_handler = logging.StreamHandler()
    log_error_handler.setLevel(logging.INFO)
    log_error_formatter = logging.Formatter("%(levelname)8s: %(message)s")
    log_error_handler.setFormatter(log_error_formatter)
    logger.addHandler(log_error_handler)
    return logger


print("Starting logger..")
logger = setup_logging()
logging_handler = LoggingHandler(
    logger=logger,
)


def lp(message, write_to_f=True, mode="info") -> None:
    if not write_to_f:
        LogMessage.Info(message)
    elif mode == "info":
        LogMessage.Info(message).write(logging_handler=logging_handler)
    elif mode == "debug":
        LogMessage.Debug(message).write(logging_handler=logging_handler)
    elif mode == "warn":
        LogMessage.Warning(message).write(logging_handler=logging_handler)
    elif mode == "crit":
        LogMessage.Critical(message).write(logging_handler=logging_handler)
    elif mode == "error":
        LogMessage.Error(message).write(logging_handler=logging_handler)
    else:
        raise ValueError("Invalid mode.")


def lrun(cmd: list, wait=True) -> None:
    if wait:
        Command(cmd).run_log_and_wait(logging_handler=logging_handler)
    else:
        Command(cmd).run_and_log(logging_handler=logging_handler)


def create_settings_file(settings) -> None:
    settings.parents[0].mkdir(parents=True, exist_ok=True)
    os.chmod(settings.parents[0], 0o755)
    lrun(
        [
            "cp",
            str(path.join(path.dirname(__file__), "data", "settings", "settings.json")),
            str(settings),
        ]
    )
    os.chmod(settings, 0o666)


def load_settings() -> JSONConfiguration:
    """
    Load the settings from the settings file

        Does the following:
        - Checks if the settings file exists
        - If not, creates it
        - If it does, loads the settings from it

        Returns:  A JSONConfiguration object
    """
    settings = Path(
        os.path.expanduser("~"), ".config", "radxa-welcome", "settings", "settings.json"
    )
    lp("Settings file: " + str(settings), mode="debug")
    if not settings.exists():
        lp("Settings file does not exist. Creating..")
        create_settings_file(settings)
    return JSONConfiguration(settings)


def settings_get(key: str, default_value: Any) -> Any:
    try:
        return app_settings[key]
    except KeyError as _:
        app_settings[key] = default_value
        app_settings.write_data()
        return default_value


def settings_set(key: str, value: Any) -> None:
    app_settings[key] = value
    app_settings.write_data()


lp("Logger started.")
lp("Setting up translations..")
_, p_ = setup_translations()  # type: ignore
lp("Translations setup.")
lp("Getting settings..")
app_settings = load_settings()

lp("Settings loaded.")
lp(app_settings, mode="debug")


def change_autolaunch(autolaunch: bool) -> None:
    """
    Change the autolaunch setting

        Does the following:
        - Changes the autolaunch setting in the settings file

        :param autolaunch:  The new autolaunch setting
        :type autolaunch: bool
    """
    app_settings["autostart"] = autolaunch
    app_settings.write_data()
    lp("Autolaunch setting changed to " + str(autolaunch), mode="info")
    if autolaunch:
        lrun(
            [
                "cp",
                "/usr/share/applications/com.radxa.welcome.desktop",
                os.path.expanduser("~") + "/.config/autostart",
            ]
        )
    else:
        lrun(
            [
                "rm",
                os.path.expanduser("~")
                + "/.config/autostart/com.radxa.welcome.desktop",
            ]
        )


# Gui support functions


def debounce(wait):
    """
    Decorator that will postpone a function's
    execution until after wait seconds
    have elapsed since the last time it was invoked.
    """

    def decorator(func):
        last_time_called = 0
        lock = Lock()

        @wraps(func)
        def debounced(*args, **kwargs):
            nonlocal last_time_called
            with lock:
                elapsed = monotonic() - last_time_called
                remaining = wait - elapsed
                if remaining <= 0:
                    last_time_called = monotonic()
                    return func(*args, **kwargs)
                else:
                    return None

        return debounced

    return decorator


def load_css(css_fn) -> Gtk.CssProvider:
    """create a provider for custom styling"""
    css_provider = None
    if css_fn and path.exists(css_fn):
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path(css_fn)
        except GLib.Error as e:
            lp(f"Error loading CSS : {e} ", mode="error")
            return None
        lp(f"loading custom styling : {css_fn}", mode="debug")
    return css_provider


def _add_widget_styling(widget, css_provider) -> None:
    if css_provider:
        context = widget.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)


def add_custom_styling(widget, css_provider) -> None:
    _add_widget_styling(widget, css_provider)
    # iterate children recursive
    for child in widget:
        add_custom_styling(child, css_provider)


# Application support functions

# {app_type: {pretty_name: [pkgname, exec_name]}}
apps = {
    "settings": {
        "Gnome Settings": ["gnome-control-center", "org.gnome.Settings"],
        "KDE settings": ["systemsettings", "kdesystemsettings"],
        "XFCE Settings": ["xfce4-settings-manager", "xfce4-settings-manager"],
        "Cinnamon Settings": ["cinnamon-settings", "cinnamon-settings"],
    },
    "terminal": {
        "Gnome Terminal": ["gnome-terminal", "org.gnome.Terminal"],
        "Konsole": ["konsole", "org.kde.konsole"],
        "XFCE4 Terminal": ["xfce4-terminal", "xfce4-terminal"],
    },
    "software_center": {
        "Gnome Software": ["gnome-software", "org.gnome.Software"],
        "Discover (KDE)": ["plasma-discover", "org.kde.discover"],
    },
    "task_manager": {
        "Gnome System Monitor": ["gnome-system-monitor", "gnome-system-monitor"],
        "KDE System Monitor": ["plasma-systemmonitor", "org.kde.plasma-systemmonitor"],
        "XFCE Task Manager": ["xfce4-taskmanager", "xfce4-taskmanager"],
    },
}


def check_app_installed(app_pkg: str) -> bool:
    """
    Check if an application is installed

        Does the following:
        - Checks if the application is installed
        - Returns True if it is, False if it is not

        :param app_pkg:  The package name of the application
        :type app_pkg: str
        :return:  Whether the application is installed
        :rtype: bool
    """
    lp(f"Checking if {app_pkg} is installed..", mode="debug")
    try:
        subprocess.check_call(
            ["dpkg", "-s", app_pkg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def install_app(app_pkg: str) -> None:
    """
    Install an application

        Does the following:
        - Installs the application using apt

        :param app_pkg:  The package name of the application
        :type app_pkg: str
    """
    lrun(["pkexec", "apt-get", "install", "-y", app_pkg])


def launch_app(app_exec: str) -> None:
    """
    Launch an application

        Does the following:
        - Launches the application

        :param app_exec:  The executable name of the application
        :type app_exec: str
    """
    lrun(["gtk-launch", app_exec], wait=False)


def make_install_app_dialog(app_type: str, window) -> Adw.MessageDialog:
    # Create a list box
    listbox = Gtk.ListBox()
    for app_name in apps[app_type].keys():
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=app_name)
        row.set_child(label)
        listbox.append(row)

    # Handle the selection of an app
    def on_row_selected(listbox, row):
        if row is not None:
            global selected_app_name
            selected_app_name = row.get_child().get_text()
            lp(f"App selected: {selected_app_name}", mode="debug")

    listbox.connect("row-selected", on_row_selected)

    def on_install_app(dialog, response_id):
        if response_id == "yes" and selected_app_name in apps[app_type]:
            app_pkg, app_exec = apps[app_type][selected_app_name]
            install_app(app_pkg)
            launch_app(app_exec)

    # Create the dialog
    dialog = Adw.MessageDialog(
        title=_("Install application"),
        body=_(
            "It seems you don't have an application for that type, which application would you like to install?"
        ),
        transient_for=window,
        default_response="yes",
        close_response="no",
        hide_on_close=True,
        extra_child=listbox,
    )
    dialog.add_response("no", _("No"))
    dialog.add_response("yes", _("Yes"))
    dialog.set_response_appearance("yes", Adw.ResponseAppearance.SUGGESTED)
    dialog.connect("response", on_install_app)

    return dialog


def check_installed(app_type: str, window) -> None:
    """
    Manage an application of the specified type

        Does the following:
        - Searches for the first app of the specified type
        - Checks if it is installed, installs it if not
        - Launches the application

        :param app_type: The type of application
        :type app_type: str
    """
    if app_type not in apps:
        raise ValueError(f"Unknown app type: {app_type}")

    for pretty_name, (pkgname, exec_name) in apps[app_type].items():
        if check_app_installed(pkgname):
            launch_app(exec_name)
            return

    dialog = make_install_app_dialog(app_type, window)
    dialog.present()
