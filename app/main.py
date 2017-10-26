from jnius import autoclass, cast
from kivy.app import App
from kivy.config import ConfigParser
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import *
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform
import main_utils
from main_utils import current_activity
import screens
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
import logging
from logging import StreamHandler

# print log info to terminal
logger = logging.getLogger('MOBILEINSIGHT ' + __name__)
logger.addHandler(StreamHandler())

# not working
# SERVICE_DIR = os.path.join(os.getcwd(), 'service')
# sys.path.append(SERVICE_DIR)

# Load main UI
Window.softinput_mode = "pan"
Window.clearcolor = (1, 1, 1, 1)
Builder.load_file('main_ui.kv')

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



#class LabeledCheckBox(GridLayout):
#    active = BooleanProperty(False)
#    text = StringProperty("")
#    group = ObjectProperty(None, allownone=True)

#    def __init__(self, **kwargs):
#        self.register_event_type("on_active")
#        super(LabeledCheckBox, self).__init__(**kwargs)
#        self.active = kwargs.get("active", False)
#        self.text = kwargs.get("text", False)
#        self.group = kwargs.get("group", None)

#    def on_active(self, *args):
#        pass

#    def callback(self, cb, value):
#        self.active = value
#        self.dispatch("on_active")


class MobileInsightApp(App):
    manager = None
    screen = None
    use_kivy_settings = False
    log_viewer = None

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

        self.manager = ScreenManager()
        self.screen = screens.HomeScreen(name='HomeScreen', screen_manager=self.manager)
        self.manager.add_widget(self.screen)

        try:
            self.log_viewer_screen = screens.LogViewerScreen(
                name='LogViewerScreen', screen_manager=self.manager)
            self.manager.add_widget(self.log_viewer_screen)
        except Exception as e:
            import crash_app
            logger.exception(traceback.format_exc())
            self.screen.ids.log_viewer.disabled = True
            self.screen.ids.stop_plugin.disabled = True
            self.screen.ids.run_plugin.disabled = True

        self.manager.current = 'HomeScreen'
        Window.borderless = False

        # return self.screen
        return self.manager

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
                import crash_app
                logger.exception(traceback.format_exc())

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
            logger.exception(traceback.format_exc())

    def on_start(self):
        from kivy.config import Config
        Config.set('kivy', 'exit_on_escape', 0)

        self.check_update()

    def on_stop(self):
        # TODO: should decouple plugin service stop from add stop
        self.screen.stop_service()

if __name__ == "__main__":
    try:
        MobileInsightApp().run()
    except Exception as e:
        import crash_app
        logger.exception(traceback.format_exc())
        crash_app.CrashApp().run()
