
# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
Desarrollado Por: Cristian M. Veliz Cano
Verción del Soft: V-02
Nombre del Soft: Video_Player_Widget_Logic_v02
Distribución: Gratuito  -->OPENSOURCE<--
'''
##=============================================================================================
##=============================================================================================

import sys, os

from PyQt5 import QtWidgets, QtGui, QtCore, QtMultimedia, QtMultimediaWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QAction, 
    QSlider, QStyle, QSizePolicy, QMenu, QLabel)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QEvent
from PyQt5.QtGui import QIcon, QFont, QPixmap, QCursor, QCloseEvent

os.add_dll_directory(os.getcwd())
os.environ['SDL_VIDEODRIVER'] = "dummy"
##=============================================================================================
##=============================================================================================
##Clase para todos, los Assets Varios
class Path():
    
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for pyinstaller"""
        try:
            #PyInstaller Create a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

##=============================================================================================
##=============================================================================================
##Clase Principal para Todos, Todos Todos los Videos, o Cualquier Video Individual
class VideoPlayerWidget(QWidget):
    # Señales:
    clicked = pyqtSignal(QWidget)         # Señal para cada click en los Botones, o Pantalla
    request_close = pyqtSignal(QWidget)   # Señal para cerrar este video

    def __init__(self, parent=None):
        super().__init__(parent)
        
        ## Evento de Cierre en la App, al precionar el Btn. Cerrar (X)
        self.closeEvent = QCloseEvent()

        # Metodo para la Captura, de los Eventos, en el Mouse (Well)
        self.setMouseTracking(True)

        self.playlist = QMediaPlaylist()

        # Bariable, para copiar, Metodo Full Screen
        self.Objeto_Video = ""
        self.file_path = ""

        # ---- MediaPlayer ----
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        # Creamos el QVideoWidget(), donde Viviran todos los Videos
        self.videoWidget = QVideoWidget()
        # Pocicionamiento Global de QVideoWidget(), esencial antes del Redimencionamiento
        self.videoWidget.setGeometry(self.pos().x(), self.pos().y(), self.width(), self.height())
        # Reacomodamos Cada Video, para que no Desproporcione
        self.videoWidget.setMinimumSize(300, 200)
        self.videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_aspect_ratio_mode(Qt.IgnoreAspectRatio)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ---- Título del video ----
        self.titleLabel = QLabel("Sin título")
        self.titleLabel.setStyleSheet("""QLabel {color: #000040; font-size: 14px; padding: 3px;
                background-color: #ff8cff;}""")
        self.titleLabel.setAlignment(Qt.AlignCenter)

        # ---- Botón Play / Pause ----
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedWidth(25)
        self.playButton.setFixedHeight(25)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.setStyleSheet('QPushButton:hover {background-color: #ffffff;}')
        self.playButton.clicked.connect(self.play)

        # ---- Botón Stop ----
        self.stopButton = QPushButton()
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedWidth(25)
        self.stopButton.setFixedHeight(25)
        self.stopButton.setStyleSheet('QPushButton:hover {background-color: #ffffff;}')
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        # ---- Botón Muted (Mudo) ----
        self.icon_muted = QIcon()
        self.btn_muted = QPushButton()
        self.btn_muted.setFixedWidth(25)
        self.btn_muted.setFixedHeight(25)
        self.muted = Path.resource_path('Ico\\volume-off.png')
        self.icon_muted.addPixmap(QPixmap(self.muted), QIcon.Normal, QIcon.Off)
        self.btn_muted.setIcon(self.icon_muted)
        self.btn_muted.setIconSize(QtCore.QSize(18, 18))
        self.btn_muted.setObjectName("btn_muted")
        self.btn_muted.setStyleSheet('QPushButton:hover {background-color: #ffffff;}')
        self.btn_muted.clicked.connect(self.Muted_Vol)
        self.stopButton.clicked.connect(self.stop)

        # --> NUEVO: Slider de Volumen (más corto) ──○── <--
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setValue(50)
        self.volumeSlider.setFixedWidth(40)
        self.volumeSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #565a5e;
                height: 8px;
                background: #565a5e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #565a5e;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::add-page:horizontal {
                background: #565a5e;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 4px;
            }
        """)
        self.volumeSlider.valueChanged.connect(self.set_volume)

        # ================================================================
        # NUEVO: Slider de posición ────────○────── con temporizador
        # ================================================================
        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #565a5e;
                height: 8px;
                background: #565a5e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #565a5e;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
            QSlider::add-page:horizontal {
                background: #565a5e;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 4px;
            }
        """)
        self.positionSlider.sliderMoved.connect(self.set_position)

        # Label´s contol Time (Status, Duration):
        self.currentTimeLabel = QLabel("00:00")
        self.currentTimeLabel.setStyleSheet("""QLabel {color: #000000; font-size: 14px;}""")
        self.totalTimeLabel = QLabel("00:00")
        self.totalTimeLabel.setStyleSheet("""QLabel {color: #000000; font-size: 14px;}""")

        # Layout:
        timeLayout = QHBoxLayout()
        timeLayout.setContentsMargins(0, 0, 0, 0)
        timeLayout.setSpacing(2)
        timeLayout.addWidget(self.currentTimeLabel)
        timeLayout.addWidget(self.positionSlider)
        timeLayout.addWidget(self.totalTimeLabel)

        # ---- Botón Menú ----
        icon_4 = QIcon()
        self.btnMenu = QPushButton()
        self.btnMenu.setFixedWidth(25)
        self.btnMenu.setFixedHeight(25)
        self.menu = Path.resource_path('Ico\\menu.png')
        icon_4.addPixmap(QPixmap(self.menu), QIcon.Normal, QIcon.Off)
        self.btnMenu.setIcon(icon_4)
        self.btnMenu.setIconSize(QtCore.QSize(18, 18))
        self.btnMenu.setStyleSheet('QPushButton:hover {background-color: #ffffff;}')
        self.btnMenu.clicked.connect(lambda: Menu_Clic.create_rightmenu(self))

        # ---- Botón Cerrar ----
        icon_5 = QIcon()
        self.closeButton = QPushButton()
        self.closeButton.setFixedWidth(25)
        self.closeButton.setFixedHeight(25)
        self.menu_close = Path.resource_path('Ico\\close.png')
        icon_5.addPixmap(QPixmap(self.menu_close), QIcon.Normal, QIcon.Off)
        self.closeButton.setIcon(icon_5)
        self.closeButton.setIconSize(QtCore.QSize(18, 18))
        self.closeButton.setStyleSheet('QPushButton:hover {background-color: #ffffff;}')
        self.closeButton.clicked.connect(self._request_close)

        # ---- Layout de controles ----
        controlsLayout = QHBoxLayout()
        controlsLayout.setContentsMargins(0, 0, 0, 0)
        controlsLayout.setSpacing(0)

        controlsLayout.addWidget(self.playButton)
        controlsLayout.addWidget(self.stopButton)

        #controlsLayout.addStretch()
        controlsLayout.addLayout(timeLayout)
        controlsLayout.addWidget(self.btn_muted)
        controlsLayout.addWidget(self.volumeSlider)
        controlsLayout.addWidget(self.btnMenu)
        controlsLayout.addWidget(self.closeButton)   # A LA DERECHA

        # ---- Layout principal ----
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.videoWidget)        
        layout.addWidget(self.titleLabel)
        layout.addLayout(controlsLayout)
        self.setLayout(layout)

        # ---- Conectar QVideoWidget, con el Evento de Full Screen y Clic IzQuierdo----
        self.videoWidget.installEventFilter(self)# Conecte a las funciones de visualización del menú
        self.videoWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.videoWidget.customContextMenuRequested.connect(lambda: Menu_Clic.create_rightmenu(self))

        # ---- Conectar MediaPlayer ----
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.media_state_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        ##Para color del Menú
        self.color_bg = str("#000000")
        self.color_color = str("blue")

        ##Para la Selección del Color en Menú
        self.color_bg_selection = str("#ffffff")
        self.color_color_selection = str("#000000")

        ##Definimos el Color del Menú, Click Izquierdo
        self.menu_color = str(f"background-color:{self.color_bg} ; color: {self.color_color} ; selection-background-color: {self.color_bg_selection} ; selection-color: {self.color_color_selection} ")

        # Create Font Size, Font Bold, Font Wieight, Font PonintSize
        self.font = QtGui.QFont()
        self.font.setPointSize(12)
        self.font.setBold(True)
        self.font.setWeight(50)

##=============================================================================================
##=============================================================================================

## Metodo para Hacer Full Screen el Widget del Video (QMediaPlayer())
## Metodo (Original), con (MouseButtonDblClick)
    def eventFilter(self, obj, event):

        ## print(event.type())
        ## print(help(QEvent))  ##<-Para Obtener Alluda Sobre Todos los Eventos en la App.-

        self.Objeto_Video = obj   ## Variable que Copia el (obj)

        if event.type() == QEvent.MouseButtonDblClick:
            obj.setFullScreen(not obj.isFullScreen())
            self.play()

        elif event.type() == QEvent.MouseButtonPress:
            self.play()

        return False

    # ============================================================
    # --------------MODO EXPANDIDO DE LOS VIDEOS  ----------------
    # ============================================================
    def set_aspect_ratio_mode(self, mode):        
        self.videoWidget.setAspectRatioMode(mode)

    # -----------------------------
    #  Señales / eventos
    # -----------------------------
    def _request_close(self):
        """Notifica a MainWindow que este video debe cerrarse."""
        self.request_close.emit(self)

    def mousePressEvent(self, event):
        if self.videoWidget.underMouse():
            self.clicked.emit(self)
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        if self.videoWidget.underMouse():
            delta = event.angleDelta().y()
            if delta > 0:
                self.volumeSlider.setValue(self.volumeSlider.value() + 5)
            else:
                self.volumeSlider.setValue(self.volumeSlider.value() - 5)
            event.accept()
        else:
            event.ignore()

    # -----------------------------
    #   Acorta el Nombre
    # -----------------------------
    def acortando_title(self, text, length=40):

        name, ext = os.path.splitext(text)

        if text:

            if len(text) <= length:
                return text

            else:
                return f"{' '.join(text[:length+1].split(' ')[0:-1])} ....{ext}"

    # -----------------------------
    #   Carga de archivo, desde Principal
    # -----------------------------
    def open_file(self, file_path):

        path_vid = os.path.isfile(file_path)
        if path_vid == True:

            self.file_path = file_path
            if file_path:
                self.playButton.setEnabled(True)
                self.mediaPlayer.stop()
                self.playlist.clear()

                # Control de reproducción de video de Qt.
                self.palylist = QMediaPlaylist()
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))

                self.mediaPlayer.setPlaylist(self.playlist)
                self.mediaPlayer.playlist().setCurrentIndex(0)
                self.stopButton.setEnabled(True)

                self.mediaPlayer.play()
                self.mediaPlayer.stop()
                self.mediaPlayer.stop()

                # Asignar título basado en el nombre del archivo
                name1 = os.path.basename(file_path)
                name = self.acortando_title(name1)
                self.titleLabel.setText(name)

        else:
            return None

    # -----------------------------
    #   Controles
    # -----------------------------
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:

            try:

                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
                self.mediaPlayer.play()

            except Exception as e:
                raise e
            

    def stop(self):
        self.mediaPlayer.stop()

    def set_volume(self, volume):
        self.mediaPlayer.setVolume(volume)

    def Muted_Vol(self):

        if self.mediaPlayer.isMuted() == True:
            self.mediaPlayer.setMuted(False)

            self.muted = Path.resource_path('Ico\\volume-off.png')
            self.icon_muted.addPixmap(QPixmap(self.muted), QIcon.Normal, QIcon.Off)
            self.btn_muted.setIcon(self.icon_muted)
            self.btn_muted.setIconSize(QtCore.QSize(18, 18))

        else:

            self.mediaPlayer.setMuted(True)

            self.muted = Path.resource_path('Ico\\volume-down.png')
            self.icon_muted.addPixmap(QPixmap(self.muted), QIcon.Normal, QIcon.Off)
            self.btn_muted.setIcon(self.icon_muted)
            self.btn_muted.setIconSize(QtCore.QSize(18, 18))

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    # -----------------------------
    #   Actualización UI
    # -----------------------------
    def media_state_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.positionSlider.setValue(position)
        self.currentTimeLabel.setText(self.format_time(position))

    def duration_changed(self, duration):
        self.positionSlider.setRange(0, duration)
        self.totalTimeLabel.setText(self.format_time(duration))

    # -----------------------------
    #   Utilidad formato de tiempo
    # -----------------------------
    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def closeEvent(self, event):
        print('Cerrando...')
        self.mediaPlayer.stop()
        self.mediaPlayer.stop()
        self._request_close()

        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: ## Key Board (Teclado - Tecla Escape (ESC))
            self._request_close()

##=============================================================================================
##=============================================================================================
##Clase Menú Clic Izquierdo
class Menu_Clic(VideoPlayerWidget):

    def __init__(self):
        super().__init__()

    def create_rightmenu(self):

        # Objeto de menú
        self.groupBox_menu = QMenu(self)
        self.groupBox_menu.setFont(self.font)
        self.groupBox_menu.setStyleSheet(self.menu_color)

        self.groupBox_menu.addSeparator()
        self.groupBox_menu.addSeparator()

        ##================================================================================================================
        ##================================================================================================================

        self.Full_Screen1 = Path.resource_path('Ico\\expand.png')
        self.Full_Screen = QAction(QIcon(self.Full_Screen1), 'Full Screen Video', self)
        self.Full_Screen.triggered.connect(lambda: full_screen_video.Full_Screen_Video(self)) 
        self.groupBox_menu.addAction(self.Full_Screen)

        self.groupBox_menu.addSeparator()
        self.groupBox_menu.addSeparator()

        ##================================================================================================================
        ##================================================================================================================

        self.groupBox_menu.popup(QCursor.pos())

##=============================================================================================
##=============================================================================================
## Clase para Hacer Full Screen el Widget del Video (QMediaPlayer())
class full_screen_video(VideoPlayerWidget):

    def __init__(self):
        super().__init__()

    ## Metodo (Copia), para poder utilizar la Tecla (F11) o (Menú-Full_Screen)
    def Full_Screen_Video(self):
        global obj_vid

        obj_vid = self.Objeto_Video  ## Variable que Copia el (obj)

        if obj_vid == self.Objeto_Video:

                obj_vid.setFullScreen(not obj_vid.isFullScreen())

##=============================================================================================
##=============================================================================================