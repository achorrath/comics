import appex
import feeddata


def main():
    url = appex.get_text()
    if url:
        try:
            feed_test = feeddata.load_feed_url(url)
        except Exception as e:
            print(str(e))
            return

        if feed_test.bozo:
            print('Add Feed failed: %s' % feed_test.bozo_exception)
            return

        feed_list = feeddata.load_feed_list()
        feed_list.append(url)
        feeddata.save_feed_list(feed_list)
        print('Saved feed: %s' % feed_test.feed.title)

if __name__ == '__main__':
    main()

