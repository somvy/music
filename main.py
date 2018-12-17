import sys
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from mainui1 import Ui_MainWindow


class MyApplication(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.playlist = QMediaPlaylist()
        self.player = QMediaPlayer()
        self.current_action = -1
        self.player.mediaStatusChanged.connect(self.status_changed)
        self.player.stateChanged.connect(self.state_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.mediaChanged.connect(self.media_changed)
        self.player.setVolume(50)
        self.init_ui()

    def init_ui(self):
        self.pushButton_Load_file.clicked.connect(self.open_file)
        self.pushButton_Load_folder.clicked.connect(self.open_folder)
        self.pushButton_Play.clicked.connect(self.play)
        self.pushButton_Next.clicked.connect(self.next_track)
        self.pushButton_Volume_plus.clicked.connect(self.volume_plus)
        self.pushButton_Volume_minus.clicked.connect(self.volume_minus)
        self.pushButton_Prev.clicked.connect(self.previous_track)
        self.pushButton_Pause.clicked.connect(self.pause)
        self.pushButton_Stop.clicked.connect(self.stop)
        self.horizontalSlider.sliderMoved.connect(self.change_position)

    def play(self):
        self.current_action = 1
        if self.player.state() == QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                if self.playlist.mediaCount() == 0:
                    self.open_file()
                if self.playlist.mediaCount() != 0:
                    self.player.setPlaylist(self.playlist)
            elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.player.play()
            elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.player.play()
        elif self.player.state() == QMediaPlayer.PlayingState:
            pass
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()

    def pause(self):
        self.current_action = 2
        self.player.pause()

    def stop(self):
        self.current_action = 0
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.stop()
        elif self.player.state() == QMediaPlayer.StoppedState:
            pass

    def previous_track(self):
        try:
            self.player.playlist().previous()
        except AttributeError:
            pass

    def next_track(self):
        try:
            self.player.playlist().next()
        except AttributeError:
            pass

    def volume_plus(self):
        current_volume = self.player.volume()
        current_volume = min(current_volume + 5, 100)
        self.player.setVolume(current_volume)

    def volume_minus(self):
        current_volume = self.player.volume()
        current_volume = max(current_volume - 5, 0)
        self.player.setVolume(current_volume)

    def open_file(self):
        required_file = QFileDialog.getOpenFileUrl(self, '*.mp3 *.wav')
        if required_file is not None:
            self.label_Track.setText('Track name')
            self.playlist.addMedia(QMediaContent(required_file[0]))

    def open_folder(self):
        required_folder = QFileDialog.getExistingDirectory(self)
        if required_folder is not None:
            tracks_iterator = QDirIterator(required_folder)
            tracks_iterator.next()
            while tracks_iterator.hasNext():
                if not tracks_iterator.fileInfo().isDir() and \
                        tracks_iterator.fileInfo().suffix() in ('mp3', 'wav') and \
                        tracks_iterator.filePath() != '.':
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(tracks_iterator.filePath())))
                tracks_iterator.next()

    def position_changed(self, position, sender_type=False):
        slider = self.horizontalSlider
        if not sender_type:
            slider.setValue(position)
        self.label_3.setText('%d:%02d' % (int(position / 60000), int((position / 1000) % 60)))

    def state_changed(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()

    def status_changed(self):
        if self.player.mediaStatus() == QMediaPlayer.LoadedMedia and self.current_action == 1:
            duration = self.player.duration()
            self.horizontalSlider.setRange(0, duration)
            self.player.play()

    def media_changed(self):
        track_name = self.player.metaData('Title')
        author_name = self.player.metaData('AlbumArtist')
        if track_name is not None:
            self.label_Track.setText(track_name)
        else:
            self.label_Track.setText('Безымянный трэк')
        if author_name is not None:
            self.label_Artist.setText(author_name)
        else:
            self.label_Artist.setText(str(self.player.duration()))
        self.label_2.setText(
            '%d:%02d' % (int(self.player.duration() / 60), int((self.player.duration()))))

    def change_position(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.player.isSeekable():
                self.player.setPosition(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = MyApplication()
    application.show()
    sys.exit(app.exec_())
