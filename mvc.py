import urwid

# UPDATE_INTERVAL = 0.1


class Model:
    results = []
    queue = []

    # def __init__(self):


class SearchInput(urwid.LineBox):
    signals = ['enter']

    def keypress(self, size, key):
        if key != 'enter':
            return super(SearchInput, self).keypress(size, key)
        self._emit('enter')


class View(urwid.WidgetWrap):
    palette = [
        ('reverted', 'black', 'white')
    ]

    def __init__(self, controller):
        self.controller = controller
        # self.search_input = SearchInput(urwid.Edit(
        #     ''), title='Search', title_align='left')
        urwid.WidgetWrap.__init__(self, self.main_window())

    def on_search_input_keypress(self, key):
        print('KEYPRESS')

    def search_input(self):
        w = SearchInput(urwid.Edit(''))
        urwid.connect_signal(w, 'enter', self.on_search_input_keypress)
        return w

    def exit_program(self, w):
        raise urwid.ExitMainLoop()

    def main_window(self):
        w = self.search_input()
        # w = urwid.LineBox(w)
        w = urwid.Filler(w, valign='top')
        return w


class Controller:
    def __init__(self):
        self.model = Model()
        self.view = View(self)

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.view.palette)
        self.loop.run()


def main():
    Controller().main()


if '__main__' == __name__:
    main()
