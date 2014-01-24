#!/usr/bin/env python
"""
Chronos - a minimal time tracker for Mac OS X
=============================================
"""
import objc
import re
import os
import sys
import time
from Foundation import *
from AppKit import *
from PyObjCTools import NibClassBuilder, AppHelper

STATUS_IMAGES = {
    'idle': 'idle.png',
    'ticking': 'ticking.png',
    }


class Chronos(NSObject):

    images = {}
    statusbar = None
    current = 'idle'
    menu = None
    timestamp = 0

    def applicationDidFinishLaunching_(self, notification):
        self._setup_icon()
        self.update_tasks()
        # Get the timer going
        start_time = NSDate.date()
        self.timer = NSTimer.alloc().\
            initWithFireDate_interval_target_selector_userInfo_repeats_(
                start_time, 5.0, self, 'tick:', None, True)
        NSRunLoop.currentRunLoop().addTimer_forMode_(
            self.timer, NSDefaultRunLoopMode)
        self.timer.fire()

    def update_tasks(self):
        path = os.environ['HOME']+'/tasks.txt'
        if not os.path.exists(path):
            self._build_menu([])
            return
        if os.stat(path).st_mtime > self.timestamp:
            tasks = map(str.strip, open(path).readlines())
            self._build_menu(tasks)

    def _build_menu(self, tasks):
        """
        Build a very simple menu containing the given `tasks`.
        There will additionally by items for stopping a task and quitting app.
        """
        self.menu = NSMenu.alloc().init()
        self._add_item('Stop work', 'idle:')
        for task in tasks:
            self._add_item(task, 'start:' if task else '')
        self._add_item('Quit', 'terminate:')
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

    def _add_item(self, label, handle):
        menuitem = NSMenuItem.alloc().\
            initWithTitle_action_keyEquivalent_(label, handle, '')
        self.menu.addItem_(menuitem)

    def _setup_icon(self):
        statusbar = NSStatusBar.systemStatusBar()
        # Create the statusbar item
        self.statusitem = \
            statusbar.statusItemWithLength_(NSVariableStatusItemLength)
        # Load all images
        for i in STATUS_IMAGES.keys():
            self.images[i] = NSImage.alloc().\
                initByReferencingFile_(STATUS_IMAGES[i])
        # Set initial image
        self.statusitem.setImage_(self.images['idle'])
        # Let it highlight upon clicking
        self.statusitem.setHighlightMode_(1)
        # Set a tooltip
        self.statusitem.setToolTip_('Track what are you working on now')

    def idle_(self, notification):
        self._log_on_switch()
        self.current = 'idle'
        self.statusitem.setImage_(self.images['idle'])

    def start_(self, ummm):
        self._log_on_switch()
        self.current = ummm.title()
        self.since = time.time()
        self.statusitem.setImage_(self.images['ticking'])

    def _log_on_switch(self):
        if self.current is not 'idle':
            log = open(os.environ['HOME']+'/tasks-log.txt', 'a')
            print >>log, self.current, ';', int(time.time() - self.since),\
                ';', self.since,\
                ';', time.strftime("%Y-%m-%d %H:%M",
                                   time.localtime(self.since))

    def tick_(self, notification):
        self.update_tasks()


def main():
    app = NSApplication.sharedApplication()
    delegate = Chronos.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == "__main__":
    main()
