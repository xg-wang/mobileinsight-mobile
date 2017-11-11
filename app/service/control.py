from kivy.logger import Logger
from kivy.lib.osc import oscAPI as osc
from mobile_insight import monitor, analyzer
from main_utils import OSCConfig
from mi2app_utils import get_cache_dir
import os
import traceback


def coord_callback(event, *args):
    # send event data to event address and app port,
    # this will be received by screens' coordinator
    Logger.info('osc SEND>: ' + str(event))
    osc.sendMsg(OSCConfig.event_addr, dataArray=[str(event),], port=OSCConfig.app_port)


class Control(object):
    ''' Controls for Mobile Insight service
    This module manages the monitor, analyzers for mobile-insight app.
    Callbacks receive osc control signal to perform the actions.
    '''
    def __init__(self):
        self.analyzers = {}
        self.callbacks = []
        cache_directory = get_cache_dir()
        log_directory = os.path.join(cache_directory, "mi2log")
        self.monitor = OnlineMonitor()
        self.monitor.set_log_directory(log_directory)
        self.monitor.set_skip_decoding(False)
        self.monitor.run()
        Logger.info('service: monitor runs')

    def osc_callback(self, msg, *args):
        '''entrance for control
        START: starts the underlying monitor
        STOP: stops the underlying monitor
        ',' separated analyzers: set the analyzers and register
        '''
        Logger.info('control <RECV: ' + msg)
        if (len(msg) < 3):
            raise Exception('no value in control message')
        value = msg[2]
        if (value == 'STOP'):
            # TODO: does monitor supports stop?
            self.monitor.stop()
        elif (value == 'START'):
            self.monitor.run()
        else:
            analyzer_names = [s for s in value.split(',') if s != '']
            self.set_analyzers(analyzer_names)

    def set_analyzers(self, names):
        # make sure there is monitor running
        if (self.monitor is None):
            raise Exception('Monitor not yet set.')

        # remove all unwanted analyzers
        names = set(names)
        keys = set(self.analyzers.keys())
        for (name in keys - names):
            self.monitor.deregister(self.analyzers[name])
            del self.analyzers[name]
        # then register all wanted but unregistered analyzers
        try:
            for (name in names - keys):
                a = getattr(analyzer, name)()
                a.set_source(self.monitor)
                a.register_coordinator_cb(coord_callback)
                self.analyzers[name] = a
        except AttributeError as error:
            Logger.error('service: Analyzer class not found ' + error)
            Logger.error(traceback.format_exc())
