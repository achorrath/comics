import dialogs
import ui

class NavBar(ui.View):
    def __init__(self, *args, **kwargs):
        if 'background_color' not in kwargs:
            kwargs['background_color'] = 'white'
        if 'border_width' not in kwargs:
            kwargs['border_width'] = 1
        if 'border_color' not in kwargs:
            kwargs['border_color'] = 'grey'
        if 'height' not in kwargs:
            kwargs['height'] = 44
        super().__init__(*args, **kwargs)

        self.b_back = ui.Button(image=ui.Image.named('iob:ios7_arrow_back_24'),
                                action=self.delegate.go_back,
                                frame=(10, 10, 24, 24))
        self.add_subview(self.b_back)

        self.b_forward = ui.Button(image=ui.Image.named('iob:ios7_arrow_forward_24'),
                                   action=self.delegate.go_forward,
                                   frame=(self.height+10, 10, 24, 24))
        self.add_subview(self.b_forward)

        self.b_share = ui.Button(image=ui.Image.named('iob:ios7_upload_outline_24'),
                                 action=self.delegate.share,
                                 frame=(self.width-self.height+10, 10, 24, 24),
                                 flex='L')
        self.add_subview(self.b_share)


class BrowserView(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.wv = ui.WebView()
        self.add_subview(self.wv)
        self.load_url = self.wv.load_url
        
        self.nb = NavBar(delegate=self)  #, background_color='blue')
        self.add_subview(self.nb)
        
        self.wv.height = self.height - self.nb.height
        self.nb.y = self.wv.height
        self.wv.flex = 'WH'
        self.nb.flex = 'WT'

    def go_back(self, sender=None):
        x = self.wv.go_back()
        
    def go_forward(self, sender=None):
        self.wv.go_forward()
        
    def share(self, sender=None):
        url = self.wv.evaluate_javascript('window.location.href')
        dialogs.share_url(url)
        

if __name__ == '__main__':
    v = BrowserView()

    v.present()
    
    # import time
    # time.sleep(10)

    v.load_url('http://omz-software.com/pythonista/')

