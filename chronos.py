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

TASK_FILE = os.environ['HOME']+'/.tasks.txt'
LOG_FILE = os.environ['HOME']+'/.tasks-log.csv'


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
        if not os.path.exists(TASK_FILE):
            self._build_menu([])
            return
        if os.stat(TASK_FILE).st_mtime > self.timestamp:
            tasks = map(str.strip, open(TASK_FILE).readlines())
            self._build_menu(tasks)

    def _build_menu(self, tasks):
        """
        Build a very simple menu containing the given `tasks`.
        There will additionally by items for stopping a task and quitting app.
        """
        self.menu = NSMenu.alloc().init()
        self.indicator = self._add_item('Not working', '')
        self._add_item('Stop work', 'idle:')
        self._add_item('Edit tasks', 'edit:')
        self._add_item('', '')
        for task in tasks:
            self._add_item(task, 'start:' if task else '')
        self._add_item('', '')
        self._add_item('Quit', 'terminate:')
        # Bind it to the status item
        self.statusitem.setMenu_(self.menu)

    def _add_item(self, label, handle):
        if label is '':
            menuitem = NSMenuItem.separatorItem()
        else:
            menuitem = NSMenuItem.alloc().\
                initWithTitle_action_keyEquivalent_(label, handle, '')
        self.menu.addItem_(menuitem)
        return menuitem

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
        self.indicator.setTitle_('Not working')

    def start_(self, ummm):
        self._log_on_switch()
        self.current = ummm.title()
        self.since = time.time()
        self.statusitem.setImage_(self.images['ticking'])
        self.indicator.setTitle_(self.current)

    def _log_on_switch(self):
        if self.current is not 'idle':
            if not os.path.exists(LOG_FILE):
                log = open(LOG_FILE, 'w')
                print >>log, "task ; duration ; epoch ; start"
            else:
                log = open(LOG_FILE, 'a')
            print >>log, self.current, ';', int(time.time() - self.since),\
                ';', self.since,\
                ';', time.strftime("%Y-%m-%d %H:%M",
                                   time.localtime(self.since))

    def tick_(self, notification):
        self.update_tasks()
        if self.current is not 'idle':
            self.indicator.setTitle_(self.current + ' for ' +
                                     str(int((time.time()-self.since)/60)) +
                                     ' minutes')

    def edit_(self, notification):
        if not os.path.exists(TASK_FILE):
            out = open(TASK_FILE, 'w')
            print >>out, ('[ProjectA] Coding\n[ProjectA] Debugging\n\n'
                          '[ProjectB] Research\n[ProjectB] Experiments\n'
                          '[ProjectB] Write-up\n')
            out.close()
        os.system('open -t ' + TASK_FILE)


def main():
    app = NSApplication.sharedApplication()
    delegate = Chronos.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()

if __name__ == "__main__":
    main()
