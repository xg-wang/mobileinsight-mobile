import kivy
kivy.require('1.4.0')

from jnius import autoclass, cast
from kivy.app import App
from kivy.logger import Logger
from kivy.config import ConfigParser, Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform
import main_utils
from main_utils import current_activity
import screens
from screens.logviewer import LogViewerScreen
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
    index = NumericProperty(-1)
    current_title = StringProperty()
    available_screens = ListProperty([])
    hierarchy = ListProperty([])

    use_kivy_settings = False

    def __init__(self, **kwargs):
        super(MobileInsightApp, self).__init__(**kwargs)
        self.title = 'MobileInsight'
        self.screens = {}
        self.available_screens = screens.__all__
        self.home_screen = None
        self.log_viewer_screen = None
        main_utils.init_libs()
        main_utils.check_security_policy()
        main_utils.setup_osc()
        main_utils.setup_service()

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

        # self.home_screen = screens.HomeScreen()
        # self.screens[0] = self.home_screen

        self.go_next_screen()

    def open_log_viewer(self):
        try:
            if self.log_viewer_screen is None:
                self.log_viewer_screen = LogViewerScreen()
            self.root.ids.sm.switch_to(self.log_viewer_screen)
            self.log_viewer_screen.onOpen()
        except Exception as e:
            Logger.exception(traceback.format_exc())
            # self.root.ids.log_viewer.disabled = True
            # self.root.ids.stop_plugin.disabled = True
            # self.root.ids.run_plugin.disabled = True

    def on_current_title(self, instance, value):
        self.root.ids.spnr.text = value

    def go_previous_screen(self):
        self.index = (self.index - 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        if screen.name != sm.current:
            sm.switch_to(screen, direction='right')
            self.current_title = screen.name

    def go_next_screen(self):
        self.index = (self.index + 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        if screen.name != sm.current:
            sm.switch_to(screen, direction='left')
            self.current_title = screen.name

    def go_screen(self, idx):
        self.index = idx
        screen = self.load_screen(idx)
        sm = self.root.ids.sm
        if screen.name != sm.current:
            sm.switch_to(self.load_screen(idx), direction='left')
            self.current_title = screen.name

    def on_current_screen(self, name):
        self.root.ids.spnr.text = name
        if name != 'LogViewerScreen':
            idx = self.available_screens.index(name)
            if idx > -1:
                self.hierarchy.append(idx)

    def go_hierarchy_previous(self):
        ahr = self.hierarchy
        if len(ahr) == 1:
            return
        if ahr:
            ahr.pop()
        if ahr:
            idx = ahr.pop()
            self.go_screen(idx)

    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = getattr(screens, self.available_screens[index])()
        self.screens[index] = screen
        return screen


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
