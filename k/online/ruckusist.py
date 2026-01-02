from k.ui import *
import k.online

import socket
from html import escape


ADDR = 'ruckusist.com'
#ADDR = 'localhost'
PORT = 42069
USER = 'k-os'
PASS = 'k-os'
BUFF = 1024

MSG_LOGOUT = 'sys|LGOUT'
MSG_CHAT = 'chat'
MSG_CHAT_ALL = 'open'


class Mod(k.online.Mod):
    def __init__(self, k):
        super().__init__(k, Panel(k, self, target(k.btn_home, 'top')))

    def init(self):
        self.sock = None

    def login(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((ADDR, PORT))
            self.sock.setblocking(False)

            if not self.send(f'{USER}:{PASS}'):
                return False

        except ConnectionRefusedError as e:
            print(e)
            #self.k.bug(e)
            return False

        except TimeoutError as e:
            print(e)
            #self.k.bug(e)
            return False

        return True

    def chat(self, msg):
        user = MSG_CHAT_ALL

        if msg.startswith('@'):
            try:
                space = msg.index(' ')
                user = msg[1:space]
                msg = msg[space+1:]

            except ValueError:
                pass

        return self.send_msg(f'{MSG_CHAT}|{user}', msg)

    def logout(self):
        self.send_msg(MSG_LOGOUT)
        self.sock.close()
        self.sock = None

    def send(self, msg):
        emsg = msg.encode()
        sent = self.sock.send(emsg)
        print(f'sent {sent}')
        if sent == 0:
            print('socket connection broken')
            return False

        return True

    def send_msg(self, msg_type, msg=None):
        if msg is None:
            return self.send(f'{msg_type}|')
        else:
            return self.send(f'{msg_type}|{msg}')

    def tick(self):
        if not self.sock:
            return

        try:
            data = self.sock.recv(BUFF)

            if data:
                if self.k.cur_panel != self.panel:
                    self.k.panel_online.img_msg.show()

                data = data.decode()
                #history = self.panel.txt_history.append_html_text
                history = self.panel.append

                if data.startswith(f'{MSG_CHAT}|'):
                    data = data[5:]
                    user = None

                    try:
                        bar = data.index('|')
                        user = data[:bar]
                        data = data[bar+1:]

                    except ValueError:
                        pass

                    if user:
                        history('<a href="chat_' + escape(user) + '">' \
                            + escape(user) + '</a>: ')
                    else:
                        history('<font color="#FF0000">???</font>: ')

                    if data.startswith('DM-> '):
                        data = data[5:]
                        history('<b>' + self.escape(data) + '</b>')
                    else:
                        history(self.escape(data))

                else:
                    history('<body bgcolor="#FF0000">' \
                        + escape(data) + '</body>')

                history('<br>')

                #history('<a href="test">just a test</a><br>')

        except BlockingIOError:
            pass

        except ConnectionResetError:
            #self.sock.close()
            self.sock = None
            self.k.panel_online.go_offline(False)

    def escape(self, txt):
        try:
            http = txt.lower().index('http')

            try:
                end = http+4 + txt[http+4:].index(' ')
            except ValueError:
                end = len(txt)

            if txt[http+4:].lower().startswith('s://') \
                    or txt[http+4:].startswith('://'):

                link = txt[http:end]

                return escape(txt[:http]) + '<a href="' + escape(link) + '">' \
                    + escape(link) + '</a>' + self.escape(txt[end:])

        except ValueError:
            pass

        return escape(txt)


class Panel(KPanel):
    def __init__(self, k, mod, anchors=ANCHOR):
        super().__init__(k, anchors)

        self.mod = mod
        self.history = ''

        self.txt_history = pygame_gui.elements.UITextBox(
            html_text='',
            #html_text='<a href="test">just a test</a><br>',
            manager=k.gui,
            container=self.container,
            anchors=ANCHOR,
            relative_rect=pygame.Rect((0, 0), (420, 300)))

        self.input = pygame_gui.elements.UITextEntryLine(
            manager=k.gui,
            container=self.container,
            anchors=target(self.txt_history, 'top'),
            relative_rect=pygame.Rect((0, 10), (420, -1)))

        self.btn_send = pygame_gui.elements.UIButton(
            text='Send',
            manager=k.gui,
            container=self.container,
            anchors=target(self.txt_history, 'top', target(self.input)),
            relative_rect=SPACER)

    def append(self, html):
        '''
        scroll_to = None

        if self.txt_history.scroll_bar:
            scroll = self.txt_history.scroll_bar
            scroll_to = scroll.scroll_position

            print(self.txt_history.scroll_bar.scroll_position)
            #print(self.txt_history.scroll_bar.top_limit)
            print(self.txt_history.scroll_bar.bottom_limit)
            #print(self.txt_history.scroll_bar.button_height)
            print(self.txt_history.scroll_bar.sliding_button.get_abs_rect())

            h = scroll.sliding_button.get_abs_rect().height

            if scroll.scroll_position + h >= scroll.bottom_limit:
                scroll_to = scroll.bottom_limit - h
        '''

        self.history += html
        self.txt_history.set_text(self.history)

        #if scroll_to is None:
        #    self.txt_history.append_html_text('')
        #else:
        #    print(f'scroll to: {scroll_to}')

        self.txt_history.append_html_text('') # scrolls to bottom

    def show(self):
        self.k.panel_online.img_msg.hide()
        super().show()

    def send(self):
        txt = self.input.get_text()
        self.mod.chat(txt)
        self.input.set_text('')

        txt = escape(txt)
        #self.txt_history.append_html_text(
        self.append(f'<font color="#00FF00">{txt}</font><br>')

    def click(self, element, target=None):
        if element == self.btn_send:
            self.send()

        elif element == self.txt_history:
            #print('here')
            #print(target)

            if target and target.startswith('chat_'):
                target = target[5:]
                self.input.set_text('@' + target + ' ' + self.input.get_text())
                self.input.focus()

    def keydown(self, key, mod):
        if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            self.send()

