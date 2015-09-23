'''
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

'''
import logging
import threading
import re

from gui.customevents import LogCustomEvent
import model.guiapi
import qt


class GUIHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self._widgets = []
        self._widgets_lock = threading.RLock()
        formatter = logging.Formatter(
            '%(levelname)s - %(asctime)s - %(name)s - %(message)s')
        self.setFormatter(formatter)

    def registerGUIOutput(self, widget):
        self._widgets_lock.acquire()
        self._widgets.append(widget)
        self._widgets_lock.release()

    def clearWidgets(self):
        self._widgets_lock.acquire()
        self._widgets = []
        self._widgets_lock.release()

    def emit(self, record):
        try:
            msg = self.format(record)
            self._widgets_lock.acquire()
            for widget in self._widgets:
                event = LogCustomEvent(msg)
                model.guiapi.postCustomEvent(event, widget)
            self._widgets_lock.release()
        except:
            self.handleError(record)


class LogConsole(qt.QVBox):
    """
    widget component used to display a log or any other content in
    a small console window
    """
    tag_regex = re.compile(r"^([a-zA-Z]*)\ \-.*", re.DOTALL)
    tag_replace_regex = re.compile(r"^(([a-zA-Z]*)\ \-)")
    tag_colors = {
        "NOTIFICATION": "#1400F2",
        "INFO": "#000000",
        "WARNING": "#F5760F",
        "ERROR": "#FC0000",
        "CRITICAL": "#FC0000",
        "DEBUG": "#0AC400",
    }

    def __init__(self, parent, caption=""):
        qt.QVBox.__init__(self, parent)
        self.setName(caption)
        self._text_edit = qt.QTextEdit(self, caption)
        self._text_edit.setTextFormat(qt.Qt.LogText)

    def customEvent(self, event):
        self.update(event)

    def update(self, event):
        if event.type() == 3131:
            self.appendText(event.text)

    def appendText(self, text):
        """
        appends new text to the console
        """
        m = self.tag_regex.match(text)
        if m is not None:
            tag = m.group(1).upper()
            colored_tag = "<font color=\"%s\"><b>[%s]</b></font> -" % (
                self.tag_colors.get(tag, "#000000"), tag)
            text = self.tag_replace_regex.sub(colored_tag, text)
        else:
            text = "<font color=\"#000000\"><b>[INFO]</b></font> - %s" % text

        self._text_edit.append(text)

    def clear(self):
        """
        Clear the console
        """
        self._text_edit.clear()

    def sizeHint(self):
        """Returns recommended size of dialog."""
        return qt.QSize(90, 30)
