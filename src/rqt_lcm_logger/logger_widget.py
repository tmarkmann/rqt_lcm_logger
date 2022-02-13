import os
import time
import subprocess

import rospy
import rospkg

from python_qt_binding import loadUi
from python_qt_binding.QtCore import qDebug, QFileInfo, Qt, qWarning, Signal, QProcess
from python_qt_binding.QtGui import QIcon, QResizeEvent
from python_qt_binding.QtWidgets import QFileDialog, QGraphicsView, QWidget


class LoggerGraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        super(LoggerGraphicsView, self).__init__()


class LoggerWidget(QWidget):

    """
    Widget for use with Bag class to display and replay bag files
    Handles all widget callbacks and contains the instance of BagTimeline for storing visualizing bag data
    """

    last_open_dir = os.getcwd()
    set_status_text = Signal(str)

    def __init__(self, context):
        """
        :param context: plugin context hook to enable adding widgets as a ROS_GUI pane, ''PluginContext''
        """
        super(LoggerWidget, self).__init__()
        rp = rospkg.RosPack()
        ui_file = os.path.join(rp.get_path('rqt_lcm_logger'), 'resource', 'Logger.ui')
        loadUi(ui_file, self, {'BagGraphicsView': LoggerGraphicsView})

        self.setObjectName('LoggerWidget')

        self.record_button.setIcon(QIcon.fromTheme('media-record'))
        self.record_button.clicked[bool].connect(self._handle_record_clicked)

        self.text.setReadOnly(True)
        
        self._recording = False
        self._log_process = None

    def message(self, msg):
        self.text.append(msg)

    def _handle_record_clicked(self):
        if self._recording:
            self._recording = False
            self.log_process.kill()
            self.record_button.setIcon(QIcon.fromTheme('media-record'))
            self.record_button.setText('Record')
            return

        # Get the bag name to record to, prepopulating with a file name based on the current date/time
        proposed_filename = time.strftime('lcmlog-%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        filename = QFileDialog.getSaveFileName(
            self, self.tr('Select name for new LCM log'), proposed_filename, self.tr('LCM log files {.lcmlog} (*.lcmlog)'))[0]

        if filename != '':
            filename = filename.strip()
            if not filename.endswith('.lcmlog'):
                filename += ".lcmlog"

            # Begin recording
            self.record_button.setIcon(QIcon.fromTheme('media-playback-stop'))
            self.record_button.setText('Stop')
            self._recording = True

            self.message("Start Recording...")
            self.log_process = QProcess()
            self.log_process.readyReadStandardOutput.connect(self.handle_stdout)
            self.log_process.readyReadStandardError.connect(self.handle_stderr)
            self.log_process.stateChanged.connect(self.handle_state)
            self.log_process.finished.connect(self.process_finished)  
            self.log_process.start("lcm-logger", [filename])

    def handle_stderr(self):
        data = self.log_process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.log_process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Recording finished.")
        self.p = None