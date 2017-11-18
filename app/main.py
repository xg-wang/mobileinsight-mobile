import kivy
kivy.require('1.4.0')

from jnius import autoclass, cast
from kivy.app import App
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.config import ConfigParser, Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty,NumericProperty,StringProperty,ListProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

import main_utils
from main_utils import current_activity
import screens
from coordinator import COORDINATOR
import datetime
import functools
import jnius
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import threading
import time
import traceback

sys.path.append('/vagrant/mi-dev/mobileinsight-mobile/app/kivymd')
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker

# not working
# SERVICE_DIR = os.path.join(os.getcwd(), 'service')
# sys.path.append(SERVICE_DIR)

# Load main UI
Window.softinput_mode = "pan"
Window.clearcolor = (1, 1, 1, 1)

def create_folder():

    cmd = ""

    mobileinsight_path = main_utils.get_mobileinsight_path()
    if not mobileinsight_path:
        return False

    try:
        legacy_mobileinsight_path = main_utils.get_legacy_mobileinsight_path()
        cmd = cmd + "mv " + legacy_mobileinsight_path + " " + mobileinsight_path + "; "
        cmd = cmd + "mv " + legacy_mobileinsight_path + "/apps/ " + mobileinsight_path + "/plugins/; "
    except:
        pass

    if not os.path.exists(mobileinsight_path):
        cmd = cmd + "mkdir " + mobileinsight_path + "; "
        cmd = cmd + "chmod -R 755 " + mobileinsight_path + "; "


    log_path = main_utils.get_mobileinsight_log_path()
    if not os.path.exists(log_path):
        cmd = cmd + "mkdir " + log_path + "; "
        cmd = cmd + "chmod -R 755 " + log_path + "; "

    analysis_path = main_utils.get_mobileinsight_analysis_path()
    if not os.path.exists(analysis_path):
        cmd = cmd + "mkdir " + analysis_path + "; "
        cmd = cmd + "chmod -R 755 " + analysis_path + "; "

    cfg_path = main_utils.get_mobileinsight_cfg_path()
    if not os.path.exists(analysis_path):
        cmd = cmd + "mkdir " + cfg_path + "; "
        cmd = cmd + "chmod -R 755 " + cfg_path + "; "

    db_path = main_utils.get_mobileinsight_db_path()
    if not os.path.exists(db_path):
        cmd = cmd + "mkdir " + db_path + "; "
        cmd = cmd + "chmod -R 755 " + db_path + "; "

    plugin_path = main_utils.get_mobileinsight_plugin_path()
    if not os.path.exists(plugin_path):
        cmd = cmd + "mkdir " + plugin_path + "; "
        cmd = cmd + "chmod -R 755 " + plugin_path + "; "

    log_decoded_path = main_utils.get_mobileinsight_log_decoded_path()
    if not os.path.exists(log_decoded_path):
        cmd = cmd + "mkdir " + log_decoded_path + "; "
        cmd = cmd + "chmod -R 755 " + log_decoded_path + "; "

    log_uploaded_path = main_utils.get_mobileinsight_log_uploaded_path()
    if not os.path.exists(log_uploaded_path):
        cmd = cmd + "mkdir " + log_uploaded_path + "; "
        cmd = cmd + "chmod -R 755 " + log_uploaded_path + "; "

    crash_log_path = main_utils.get_mobileinsight_crash_log_path()
    if not os.path.exists(crash_log_path):
        cmd = cmd + "mkdir " + crash_log_path + "; "
        cmd = cmd + "chmod -R 755 " + crash_log_path + "; "

    # cmd = cmd + "chmod -R 755 "+mobileinsight_path+"; "
    Logger.info('main: create folder cmd: ' + cmd)
    main_utils.run_shell_cmd(cmd)
    return True


def get_plugins_list():
    '''
    Load plugin lists, including both built-in and 3rd-party plugins
    '''

    ret = {}  # app_name->(path,with_UI)

    APP_DIR = os.path.join(
        str(current_activity.getFilesDir().getAbsolutePath()), "app/plugins")
    l = os.listdir(APP_DIR)
    for f in l:
        if os.path.exists(os.path.join(APP_DIR, f, "main.mi2app")):
            # ret.append(f)
            ret[f] = (os.path.join(APP_DIR, f), False)

    # Yuanjie: support alternative path for users to customize their own plugin
    APP_DIR = main_utils.get_mobileinsight_plugin_path()

    if os.path.exists(APP_DIR):
        l = os.listdir(APP_DIR)
        for f in l:
            if os.path.exists(os.path.join(APP_DIR, f, "main_ui.mi2app")):
                if f in ret:
                    tmp_name = f + " (plugin)"
                else:
                    tmp_name = f
                ret[tmp_name] = (os.path.join(APP_DIR, f), True)
            elif os.path.exists(os.path.join(APP_DIR, f, "main.mi2app")):
                if f in ret:
                    tmp_name = f + " (plugin)"
                else:
                    tmp_name = f
                ret[tmp_name] = (os.path.join(APP_DIR, f), False)
    else:  # create directory for user-customized apps
        create_folder()

    return ret


class MobileInsightApp(App):
    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    title = "MobileInsight"

    index = NumericProperty(1)
    current_title = StringProperty()
    screen_names = ListProperty([])

    use_kivy_settings = False

    def __init__(self, **kwargs):
        super(MobileInsightApp, self).__init__(**kwargs)
        self.title = 'MobileInsight'
        self.screens = {}
        self.available_screens = screens.__all__
        self.home_screen = None
        self.log_viewer_screen = None
        if not main_utils.is_rooted():
            Logger.error(
                "MobileInsight requires root privilege. Please root your device for correct functioning.")
        if not main_utils.check_diag_mode():
            Logger.error(
                "The diagnostic mode is disabled. Please check your phone settings.")
        if not create_folder():
            # MobileInsight folders unavailable. Add warnings
            Logger.error("main: SDcard is unavailable. Please check.")
        main_utils.init_libs()
        main_utils.check_security_policy()
        COORDINATOR.start()

    def build_settings(self, settings):

        with open("settings.json", "r") as settings_json:
            settings.add_json_panel(
                'General', self.config, data=settings_json.read())

        self.create_app_settings(self.config, settings)

    def create_app_settings(self, config, settings):
        app_list = get_plugins_list()
        for app in app_list:
            APP_NAME = app
            APP_DIR = app_list[app][0]
            setting_path = os.path.join(APP_DIR, "settings.json")
            if os.path.exists(setting_path):
                with open(setting_path, "r") as settings_json:
                    raw_data = settings_json.read()

                    # Regulate the config into the format that kivy can accept
                    tmp = eval(raw_data)

                    result = "["
                    default_val = {}

                    for index in range(len(tmp)):
                        if tmp[index]['type'] == 'title':
                            result = result + '{"type": "title","title": ""},'
                        elif tmp[index]['type'] == 'options':
                            default_val[tmp[index]['key']
                                        ] = tmp[index]['default']
                            result = result + '{"type": "' + tmp[index]['type'] \
                                + '","title":"' + tmp[index]['title'] \
                                + '","desc":"' + tmp[index]['desc'] \
                                + '","section":"' + APP_NAME \
                                + '","key":"' + tmp[index]['key'] \
                                + '","options":' + json.dumps(tmp[index]['options']) \
                                + '},'
                        else:
                            default_val[tmp[index]['key']
                                        ] = tmp[index]['default']
                            result = result + '{"type": "' + tmp[index]['type'] \
                                + '","title":"' + tmp[index]['title'] \
                                + '","desc":"' + tmp[index]['desc'] \
                                + '","section":"' + APP_NAME \
                                + '","key":"' + tmp[index]['key'] \
                                + '"},'
                    result = result[0:-1] + "]"

                    # Update the default value and setting menu
                    settings.add_json_panel(APP_NAME, config, data=result)

    def build_config(self, config):
        # Yuanjie: the ordering of the following options MUST be the same as
        # those in settings.json!!!
        config.setdefaults('mi_general', {
            'bcheck_update': 0,
            'log_level': 'info',
            'bstartup': 0,
            'bstartup_service': 0,
            'bgps': 1,
            'start_service': 'NetLogger',
        })
        self.create_app_default_config(config)

    def create_app_default_config(self, config):
        app_list = get_plugins_list()
        for app in app_list:
            APP_NAME = app
            APP_DIR = app_list[app][0]
            setting_path = os.path.join(APP_DIR, "settings.json")
            if os.path.exists(setting_path):
                with open(setting_path, "r") as settings_json:
                    raw_data = settings_json.read()

                    # Regulate the config into the format that kivy can accept
                    tmp = eval(raw_data)

                    default_val = {}

                    for index in range(len(tmp)):
                        if tmp[index]['type'] == 'title':
                            pass
                        elif 'default' in tmp[index]:
                            default_val[tmp[index]['key']
                                        ] = tmp[index]['default']

                    # Update the default value and setting menu
                    config.setdefaults(APP_NAME, default_val)

    def build(self):
        # Force to initialize all configs in .mobileinsight.ini
        # This prevents missing config due to existence of older-version .mobileinsight.ini
        # Work-around: force on_config_change, which would update config.ini
        config = self.load_config()
        val = int(config.get('mi_general', 'bcheck_update'))
        config.set('mi_general', 'bcheck_update', int(not val))
        config.write()
        config.set('mi_general', 'bcheck_update', val)
        config.write()

        Window.borderless = False

        self.screens = {}
        self.available_screens = screens.__all__
        self.screen_names = self.available_screens
        for i in range(len(self.available_screens)):
            self.screens[i] = getattr(screens, self.available_screens[i])()
        COORDINATOR.setup_analyzers()
        COORDINATOR.send_control('START')
        self.root.ids.scr_mngr.switch_to(self.screens[0])

    def go_screen(self, idx):
        self.index = idx
        self.root.ids.scr_mngr.switch_to(self.load_screen(idx), direction='left')
        if idx == 7:
            self.screens[7].onOpen()

    def load_screen(self, index):
        return self.screens[index]

    def get_time_picker_data(self, instance, time):
        self.root.ids.time_picker_label.text = str(time)
        self.previous_time = time

    def show_example_time_picker(self):
        self.time_dialog = MDTimePicker()
        self.time_dialog.bind(time=self.get_time_picker_data)
        if self.root.ids.time_picker_use_previous_time.active:
            try:
                self.time_dialog.set_time(self.previous_time)
            except AttributeError:
                pass
        self.time_dialog.open()

    def set_previous_date(self, date_obj):
        self.previous_date = date_obj
        self.root.ids.date_picker_label.text = str(date_obj)

    def show_example_date_picker(self):
        if self.root.ids.date_picker_use_previous_date.active:
            pd = self.previous_date
            try:
                MDDatePicker(self.set_previous_date,
                             pd.year, pd.month, pd.day).open()
            except AttributeError:
                MDDatePicker(self.set_previous_date).open()
        else:
            MDDatePicker(self.set_previous_date).open()

    def set_error_message(self, *args):
        if len(self.root.ids.text_field_error.text) == 2:
            self.root.ids.text_field_error.error = True
        else:
            self.root.ids.text_field_error.error = False

    def on_pause(self):
        # Yuanjie: The following code prevents screen freeze when screen off ->
        # screen on
        try:
            pm = current_activity.getSystemService(
                autoclass('android.content.Context').POWER_SERVICE)
            if not pm.isInteractive():
                current_activity.moveTaskToBack(True)
        except Exception as e:
            try:
                # API 20: pm.isScreenOn is depreciated
                pm = current_activity.getSystemService(
                    autoclass('android.content.Context').POWER_SERVICE)
                if not pm.isScreenOn():
                    current_activity.moveTaskToBack(True)
            except Exception as e:
                Logger.exception(traceback.format_exc())

        # print "on_pause"
        return True  # go into Pause mode

    def on_resume(self):
        # print "on_resume"
        pass

    def check_update(self):
        """
        Check if new update is available
        """
        try:
            config = ConfigParser()
            config.read('/sdcard/.mobileinsight.ini')
            bcheck_update = config.get("mi_general", "bcheck_update")
            if bcheck_update == "1":
                import check_update
                check_update.check_update()
        except Exception as e:
            Logger.exception(traceback.format_exc())

    def on_start(self):
        Config.set('kivy', 'exit_on_escape', 0)

        self.check_update()

    def on_stop(self):
        main_utils.stop_osc()
        main_utils.stop_service()
        # TODO: should decouple plugin service stop from add stop
        # self.home_screen.stop_service()
        sm = self.root.ids.sm
        sm.current_screen.coordinator.stop()


if __name__ == "__main__":
    try:
        MobileInsightApp().run()
    except Exception as e:
        import crash_app
        Logger.exception(traceback.format_exc())
        crash_app.CrashApp().run()
