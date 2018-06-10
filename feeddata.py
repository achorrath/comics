import collections
import datetime
import feedparser
import json
import requests
import time

save_name = 'feeds.json'


def load_feed_url(url):
    resp = requests.get(url, timeout=5.0)
    feed = feedparser.parse(resp.content)
    return feed


def load_feed_list():
    with open(save_name) as save_file:
        feed_list = json.load(save_file)
    return feed_list


def save_feed_list(feed_list):
    with open(save_name, 'w') as save_file:
        json.dump(feed_list, save_file)


class Feed(object):
    def __init__(self, url):
        self.url = url
        self.raw_data = None
        self.error = None
        self.feed = None
        self.entries = None

        try:
            self.raw_data = load_feed_url(url)
        except Exception as e:
            self.error = str(e)
            return

        if self.raw_data and self.raw_data.bozo:
            self.error = self.raw_data.bozo_exception
            return

        self.feed = self.raw_data.feed
        self.entries = self.raw_data.entries


class FeedData(object):
    def __init__(self):
        self.feeds = []
        self.entries_by_date = collections.defaultdict(list)
        self.ordered_dates = []
        self.loaded = False

    def load(self, callback=None):
        if self.loaded:
            return
        else:
            self.loaded = True

        try:
            saved_urls = load_feed_list()
        except:
            return
        for url in saved_urls:
            self.add_feed_url(url)
            if callback:
                callback()

    def save(self):
        if self.loaded:
            save_feed_list([f.url for f in self.feeds])

    def add_feed_url(self, url):
        feed = Feed(url)
        self.feeds.append(feed)
        if feed.error:
            return
        for e in feed.entries:
            try:
                key = datetime.date.fromtimestamp(time.mktime(e.published_parsed))
            except:
                key = datetime.date.fromtimestamp(0)
            self.entries_by_date[key].append(e)
        self.ordered_dates = sorted(self.entries_by_date.keys(), reverse=True)
        
    def remove_feed_index(self, index):
        old = self.feeds.pop(index)
        if old.error:
            return
        for e in old.entries:
            try:
                key = datetime.date.fromtimestamp(time.mktime(e.published_parsed))
            except:
                key = datetime.date.fromtimestamp(0)
            self.entries_by_date[key].remove(e)
        for key in list(self.entries_by_date):
            if self.entries_by_date[key] == []:
                del self.entries_by_date[key]
        self.ordered_dates = sorted(self.entries_by_date.keys(), reverse=True)
        
    def move_feed(self, old_index, new_index):
        feed = self.feeds.pop(old_index)
        self.feeds.insert(new_index, feed)

