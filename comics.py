import browser
import feeddata
import dialogs
import ui

myfeeddata = feeddata.FeedData()

def get_control_width(control):
    maxwidth = 0
    for segment in control.segments:
        tmp = ui.Button()
        tmp.title = segment
        tmp.size_to_fit()
        maxwidth = max(maxwidth, tmp.width)
    return 2 * maxwidth * len(control.segments)

#
# TableView of the entries for a single feed
#
class EntriesDataSource(object):
    def __init__(self, feed):
        self.feed = feed  # feeddata.Feed

    def tableview_number_of_sections(self, tableview):
        return 1

    def tableview_number_of_rows(self, tableview, section):
        return len(self.feed.entries)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell()
        cell.accessory_type = 'detail_button'
        cell.text_label.text = self.feed.entries[row].title
        return cell

    def tableview_can_delete(self, tableview, section, row):
        return False

    def tableview_can_move(self, tableview, section, row):
        return False

    def tableview_accessory_button_tapped(self, tableview, section, row):
        entry = self.feed.entries[row]
        fields = []
        for name in ['title', 'link', 'description', 'published', 'id']:
            if name in entry:
                field = {'type': 'text',
                         'title': name.title(),
                         'value': entry[name]}
                fields.append(field)
        dialogs.form_dialog(title='Info', fields=fields)

    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        entry = self.feed.entries[row]
        tableview.selected_row = -1
        if 'link' in entry:
            panel = browser.BrowserView(name=self.feed.entries[row].title)
            panel.load_url(self.feed.entries[row].link)
            root.push_view(panel)


#
# TableView of all the feeds
#
class FeedDataSource (object):
    save_name = 'feeds.json'

    def __init__(self, myfeeddata, tableview):
        self.feeddata = myfeeddata  # feeddata.Feeddata
        self.feeds = self.feeddata.feeds
        self.tableview = tableview

    # TableView data_source methods
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections (defaults to 1)
        return 1

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        return len(self.feeds)

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        cell = ui.TableViewCell()
        cell.accessory_type = 'detail_button'
        if self.feeds[row].error:
            cell.text_label.text = str(self.feeds[row].error)
            cell.text_label.text_color = 'red'
        else:
            cell.text_label.text = self.feeds[row].feed.title
        return cell

    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return True

    def tableview_delete(self, tableview, section, row):
        self.feeddata.remove_feed_index(row)
        self.feeddata.save()
        tableview.reload_data()

    def tableview_can_move(self, tableview, section, row):
        # Return True if a reordering control should be shown for the given row (in editing mode).
        return True

    def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
        self.feeddata.move_feed(from_row, to_row)
        self.feeddata.save()

    # TableView delegate methods
    def tableview_accessory_button_tapped(self, tableview, section, row):
        feed = self.feeds[row]
        fields = [{'type': 'url',
                   'title': 'URL',
                   'value': feed.url}]
        if feed.error:
            fields.append({'type': 'text',
                           'title': 'Error',
                           'value': str(feed.error)})
        else:
            for name in ['title', 'link', 'description', 'published']:
                if name in feed.feed:
                    field = {'type': 'text',
                             'title': name.title(),
                             'value': feed.feed[name]}
                    fields.append(field)
        dialogs.form_dialog(title='Info', fields=fields)

    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        tableview.selected_row = -1
        if self.feeds[row].error:
            return
        panel = ui.TableView(name = self.feeds[row].feed.title)
        panel.data_source = EntriesDataSource(self.feeds[row])
        panel.delegate = panel.data_source
        root.push_view(panel)

    # ButtonItem methods
    def add_feed_url(self, sender):
        url = 'http://skin-horse.com/feed/'
        fields = [{'type': 'url',
                   'title': 'URL',
                   'key': 'url',
                   'value': url}]
        input = dialogs.form_dialog(title='Add Feed', fields=fields)
        if input is None or input['url'] == '':
            return
        self.feeddata.add_feed_url(input['url'])
        self.feeddata.save()
        self.superview.reload_data()

view1 = ui.TableView(frame=(0, 40, 200, 160), name='By Feed', flex='WH')
view1_source = FeedDataSource(myfeeddata, view1)
view1.data_source = view1_source
view1.delegate = view1_source
view1.editable = True

#
# TableView of all entries by date
#
class DateDataSource (object):
    def __init__(self, myfeeddata, tableview):
        self.feeddata = myfeeddata
        self.tableview = tableview

    # TableView data_source methods
    def tableview_number_of_sections(self, tableview):
        # Return the number of sections (defaults to 1)
        return len(self.feeddata.ordered_dates)

    def tableview_number_of_rows(self, tableview, section):
        # Return the number of rows in the section
        section_key = self.feeddata.ordered_dates[section]
        return len(self.feeddata.entries_by_date[section_key])

    def tableview_title_for_header(self, tableview, section):
        # Return a title for the given section.
        # If this is not implemented, no section headers will be shown.
        section_key = self.feeddata.ordered_dates[section]
        return '{dt:%A} {dt:%B} {dt.day}, {dt.year}'.format(dt=section_key)

    def tableview_cell_for_row(self, tableview, section, row):
        # Create and return a cell for the given section/row
        cell = ui.TableViewCell()
        cell.accessory_type = 'detail_button'
        section_key = self.feeddata.ordered_dates[section]
        section_data = self.feeddata.entries_by_date[section_key]
        cell.text_label.text = section_data[row].title
        return cell

    def tableview_can_delete(self, tableview, section, row):
        # Return True if the user should be able to delete the given row.
        return False

    def tableview_can_move(self, tableview, section, row):
        # Return True if a reordering control should be shown for the given row (in editing mode).
        return False

    # TableView delegate methods
    def tableview_accessory_button_tapped(self, tableview, section, row):
        section_key = self.feeddata.ordered_dates[section]
        section_data = self.feeddata.entries_by_date[section_key]
        entry = section_data[row]
        fields = []
        for name in ['title', 'link', 'description', 'published', 'id']:
            if name in entry:
                field = {'type': 'text',
                         'title': name.title(),
                         'value': entry[name]}
                fields.append(field)
        dialogs.form_dialog(title='Info', fields=fields)

    def tableview_did_select(self, tableview, section, row):
        # Called when a row was selected.
        section_key = self.feeddata.ordered_dates[section]
        section_data = self.feeddata.entries_by_date[section_key]
        entry = section_data[row]
        if 'link' in entry:
            panel = browser.BrowserView(name=section_data[row].title)
            panel.load_url(section_data[row].link)
            root.push_view(panel)


view2 = ui.TableView(frame=(0, 40, 200, 160), name='By Date', flex='WH')
view2_data = DateDataSource(myfeeddata, view2)
view2.data_source = view2_data
view2.delegate = view2_data
view2.editable = False


#
# Custom view for switching between tabs
#
class TabView(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.control = ui.SegmentedControl(flex='LR')
        self.control.y = 4
        self.control.action = self.select_subview
        self.add_subview(self.control)
        self.display_subviews = []

        self.add_button = ui.ButtonItem('Add', action=view1_source.add_feed_url)
        #self.left_button_items = [self.add_button]

        self.edit_button = ui.ButtonItem('Edit', action=self.set_editing)
        #self.right_button_items = [self.edit_button]

        self.done_button = ui.ButtonItem('Done', action=self.unset_editing)
        
    def select_subview(self, sender):
        selected = self.display_subviews[sender.selected_index]
        selected.bring_to_front()
        self.edit_button.enabled = selected.editable
        selected.reload_data()
        
    def add_subview(self, view):
        super().add_subview(view)
        if view is self.control:
            return
        self.display_subviews.append(view)
        selected = self.control.selected_index
        self.control.segments += (view.name,)
        if selected < 0:
            self.control.selected_index = 0
        else:
            self.control.selected_index = selected
        self.control.width = get_control_width(self.control)
        offset = self.control.height + 8
        view.frame = (self.x, offset, self.width, self.height - offset)
        self.display_subviews[self.control.selected_index].bring_to_front()

    def reload_data(self):
        for view in self.display_subviews:
            view.reload_data()
    
    def set_editing(self, sender):
        self.control.enabled = False
        self.left_button_items = []
        self.right_button_items = [self.done_button]
        selected = self.display_subviews[self.control.selected_index]
        selected.set_editing(True)

    def unset_editing(self, sender):
        self.control.enabled = True
        self.left_button_items = [self.add_button]
        self.right_button_items = [self.edit_button]
        selected = self.display_subviews[self.control.selected_index]
        selected.set_editing(False)


tabview = TabView(name='Comics', bg_color='white')
tabview.add_subview(view1)
tabview.add_subview(view2)

root = ui.NavigationView(tabview)
root.present()

@ui.in_background
def load():
    ai = ui.ActivityIndicator(background_color='black')
    ai.style = ui.ACTIVITY_INDICATOR_STYLE_WHITE_LARGE
    ai.present('sheet', hide_title_bar=True, animated=False)
    ai.start()
    myfeeddata.load(callback=tabview.reload_data)
    ai.stop()
    ai.close()
    tabview.unset_editing(None)

load()

