#!/usr/bin/env python2.7

import cPickle
import datetime
import os
import sys
import time

from datetime import datetime, timedelta

PICKLE_FILE = "stats_state"

class Dice_Roll_Stats:
    """
        Keep the past X hours of dice rolls
    """

    _save_state = True
    hours = {}
    stats_timer = datetime.fromtimestamp(0)
    current = {}
    stats = {}

    TIMER_AGE = timedelta(0,seconds=5)
        

    def __init__(self, size=20, state_file=PICKLE_FILE):
        self._state_file = state_file
        self.size = size
        if state_file != None:
            self._load_state()
        self._populate_stats()


    def _populate_stats(self, force=False):
        """ sum up what we need to """
        cur_time = datetime.utcnow()
        if force or ((self.stats_timer + self.TIMER_AGE) <= cur_time):
            self.stats_timer = cur_time
            stats = {}
            stats["rolls"] = 0
            stats["sum"] = 0
            stats["rolls_hour"] = []
            stats["rolls_vals"] = [0] * self.size

            rolls = self.hours.keys()
            rolls.sort()

            for i in rolls:
                rollhour = self.hours[i]
                stats["rolls"] += rollhour.totalrolls
                stats["sum"] += rollhour.totalsums
                stats["rolls_hour"].append(rollhour.totalrolls)
                for i in xrange(self.size):
                    stats["rolls_vals"][i] += rollhour.rolls[i]
            self.stats = stats
            self._save_state()


    def _load_state(self):
        if os.path.exists(self._state_file):
            self.hours = cPickle.load(open(self._state_file))
        else:
            print >>sys.stderr, "no such state file %s" % self._state_file

    def _save_state(self):
        """ 
            We just really need to save the contents of self.hours
        """
        cPickle.dump(self.hours, open(self._state_file, "w"))


    def _hour(self):
        """ give me the latest hour with truncated minutes/seconds"""
        cur = datetime.utcnow()
        trunc = datetime(cur.year,
                         cur.month,
                         cur.day,
                         cur.hour)
        return trunc


    def increment(self, value):
        """ Increment internal counter """
        curhour = self._hour()
        force = False
        if not self.hours.has_key(curhour):
            self.hours[curhour] = Struct_Roll_Count(self.size)

            # cycling out the BS
            older_hours = curhour - timedelta(1)
            for i in self.hours.keys():
                if i <= older_hours:
                    del(self.hours[i])
            force = True


        self.hours[curhour].addval(value)
        self._populate_stats(force)

    def grab_stats(self, force=False):
        """
            return a dict type that looks like:
            { rolls: 10000,
              average: 10.501,
              rolls_per_hour: [ 1000, 1001, ...]
              rolls_per_value: [ 0, 1000, 1001, ...]
            }
        """
        self._populate_stats(force)
        return self.stats


class Struct_Roll_Count:
    """
        Track stats for a period of time
    """

    rolls = []
    size = 0
    totalrolls = 0
    totalsums = 0

    def __init__(self, size):
        self.rolls = [0] * (size + 1)
        self.size = size

    def addval(self, val):
        if val > (self.size) or val < 1:
            # ignore and move on
            return
        self.rolls[val] += 1
        self.totalrolls += 1
        self.totalsums += val

