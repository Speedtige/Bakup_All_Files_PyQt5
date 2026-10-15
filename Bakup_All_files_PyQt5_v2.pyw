
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Desarrollador: Cristian M. Veliz Cano
Nombre del Soft: Bakup_All_files_PyQt5
Verción del Soft-Ware:  v_02
Distribución:  Gratuita
Interfaz: PyQt5
Lenguaje Computaciónal: Python 3.8.3

Vreve Descripción:
  Interfaz PyQt5 (single-file) para insertar archivos en una DB SQLite (tabla new_employee)
  y extraerlos. Incluye control de archivos temporales (TempFileManager)
  con borrado automático al cerrar y reintentos.

Descripción General: Crear un Bakup de nuestros Archivos Importantes y Poder Recuperarlos luego ya siendo de Uno en Uno O Todos Juntos.
Base de Datos creada en: SQlite3, pero es aplicable a MySQL Siempre con ligeros Cambios en los Lenguajes MySQL y SQLite3
Leguage de Programación en: PYTHON 3.8.3
Enpaquetado con: Auto-Py-To-Exe.exe
En la Tecnologia de -> El Original en: TKinter <-> Pero para esta Verción se adapta A: PyQt5 Sin el (designer.exe)
Uso de la Base de Datos que se Escoge: PORTATIVILIDAD, ESTAVILIDAD, CONFIANZA, ENTRE MUCHOS OTROS MAS.
Extra: La base de datos que se escogio, tambien es porque esta no NECESITA de ningun SOFT-WARE, ajeno.

Con la necesidad de ir almacenando en algun medio, nuestros, Archivos (.txt, etc, etc, etc.), o Nuestros Videos, o 
Nuestras Imagenes o Tracks (Archivos de Audio).
Podremos ir almacenandolas Tambien dentro de Nuestras Bases de Datos Especificamente, creadas para ese fin
o Proposito.
Blob, nos Ofrece una Variedad, para ese fin siendo estos:

TINYBLOB        = 255 byts
BLOB            = 65,535 byts
MEDIUMBLOB      = 16,777,215 byts
LONGBLOB        = 4,294,967,295 byts

Y En el Caso de Texto, esto:

Los cuatro tipos de texto son TinyText, Text, MediumText y LongText
Las columnas de blob y texto no pueden tener valores predeterminados
Mapa de Varchar largo y largo al tipo de datos MediumText. Esta es una característica de compatibilidad.
El conector MySQL/ODBC define los valores de blob como valores longvarbinary y de texto como longvarchar.
Debido a que los valores de blob y texto pueden ser extremadamente largos, puede encontrar algunas 
restricciones al usarlos.

Pero:

Para el Soft-Ware (PROGRAMA) de hoy lo haremos con LONGBLOB, para Crear un Bakup Con los Sig. Formatos
(".mp3"), (".png"), (".jpg"), (".mp4"), (".pdf"), (".docx"),(".xlsx"), (".rar"), (".7z"), (".zip")
y (".txt") etc. etc. es decir para que pueda almacenar casi TODOS, TODOS LOS ARCHIVOS, pero ojo que no podra
ingresarlos todos pues todo depende en como se hallan creado, es decir con que tipo de bits, (CODIFICACIÓN),
por ejemplo en el caso de Texto Plano (*.txt) hay varios tipos pero un de los mas comunes es el "utf-8",
y este necesita si o si un trato especial ya que lo estamos tratando con LONGBLOB, en lugar de LongText (longvarchar)
en fin, dependiendo con que codificacion se halla realizado. Este si Podra o no Ingresarlos dentro de la tabla
LONGBLOB, que es la que tendremos en uso. de no poder ingresar el dato, Tratara si, pero dejara un espacio,
en tabla (NONE), que a la larga perjudicaria, a la hora de la Recuperación de nuestros archivos, pero hoy no,
con este ejemplo de BAKUP, no sera hasi. Esto es aplicable, Tanto para MySQL, como en SQLite3, 
Siempre con ligeros Cambios en los Lenguajes MySQL y SQLite3.

Pero por Portativilidad, y que no Requiere de Ningun Soft-Ware Externo, se Opta Por SQLite3.-

Con esta Obción podremos, Tambien Crearlos donde los Necesitemos y podemos Recuperarlos en el momento,
que lo Deseemos, y en el Directorio que Deseemos, de Uno en Uno O Todos Juntos, Como lo Muestra el Ejemplo 
de Acontinuación,.-

'''
##=========================================================================================
##=========================================================================================

import io, os, sys
import sqlite3
import time
import tempfile
import atexit
from datetime import datetime
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np
import cv2
import time
import subprocess
import zipfile
import rarfile
import py7zr
import webbrowser
import shutil
import imutils
## from temp_file_manager import temp_file_manager
## temp_file_manager.register(path)

##=========================================================================================
##=========================================================================================

from PyQt5 import QtCore, QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QPushButton, QTextEdit, QPlainTextEdit, QFileDialog, QMessageBox, QComboBox, QLabel, QStatusBar, 
    QFrame, QStyle, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QUrl, QTimer, QEvent
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette, QColor, QBrush, QFontDatabase
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget

from stability_patch_v1 import protect_window, monitor_timer, log_message
# Importamos la clase del reproductor desde tu módulo
from Video_Player_Widget_Logic_v2 import VideoPlayerWidget

##=========================================================================================
##=========================================================================================
bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath( os.path.dirname(__file__) ) )
dir_Sumatra = os.path.join(bundle_dir, "SumatraPDF.dll",)
print(dir_Sumatra)
sumatra_pdf_path = fr"{dir_Sumatra}"  # Ajusta la ruta

# SQL TABLE
DB_TABLE_SQL = """CREATE TABLE IF NOT EXISTS new_employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, files BLOB )"""

## Forma 1 - para localizar la Carpeta ('Files_Extención'), dentro de la App. en el Dir Raiz
bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath( os.path.dirname(__file__) ) )
directory1 = os.path.join(bundle_dir, "Files_Extención",)
directory = directory1+'\\'
##=========================================================================================
##=========================================================================================

class Path():
    
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for pyinstaller"""
        try:
            #PyInstaller Create a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

# ======================================================================================
# SISTEMA DE LOG SEGURO (print + archivo)
# ======================================================================================

LOG_FILE = "stable_log.txt"
def log_message(level, message):
    """Escribe en consola y en archivo."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

##=========================================================================================================
##=========================================================================================================

def open_pdf_with_sumatra(self, pdf_path, pagina=0):

    if os.path.exists(sumatra_pdf_path):

        try:
            # Construye el comando para abrir Sumatra con la opción de página específica.
            comando = [sumatra_pdf_path, "-page", str(pagina), pdf_path]
            out_path = subprocess.Popen(comando)  # Usa Popen para que no espere a que se cierre Sumatra
            temp_file_manager.register(out_path)            

        except FileNotFoundError:
            print(f"Error: SumatraPDF.exe no encontrado. Asegúrate de que está en el PATH o proporciona la ruta completa.")

        except Exception as e:
            print(f"Error al abrir Sumatra PDF: {e}")

    else:
        print("No se encuentra SumatraPDF en la ruta especificada.")

# ======================================================================================
# FUNCIONES DE UTILIDAD
# ======================================================================================

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)
    return path

def append_to_file(path, text):
    """Escribe texto simple en archivo log local."""
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + os.linesep)
    except Exception as e:
        log_message("ERROR", f"Fallo al escribir {path}: {e}")

# ======================================================================================
# GESTOR DE ARCHIVOS TEMPORALES
# ======================================================================================

class TempFileManager:
    """Administra archivos temporales con registro y borrado seguro."""
    def __init__(self):
        self._files = set()
        atexit.register(self.delete_all)

    def register(self, path):
        if path:
            self._files.add(os.path.abspath(path))
            log_message("INFO", f"Registrado temporal: {path}")

    def unregister(self, path):
        if path:
            self._files.discard(os.path.abspath(path))

    def delete_with_retries(self, path, retries=6, delay=0.25):
        """Intenta borrar el archivo con varios intentos."""
        if not path:
            return False
        p = os.path.abspath(path)
        for i in range(retries):
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                elif os.path.exists(p):
                    os.remove(p)
                if not os.path.exists(p):
                    self._files.discard(p)
                    log_message("INFO", f"Temporal eliminado: {p}")
                    return True
            except Exception as e:
                log_message("WARN", f"Intento {i+1} fallido al borrar {p}: {e}")
                time.sleep(delay)
        return False

    def delete_all(self):
        """Borra todos los archivos registrados (también en atexit)."""
        for p in list(self._files):
            self.delete_with_retries(p)
        self._files.clear()
        log_message("INFO", "Limpieza global de temporales completada.")

# Instancia global
temp_file_manager = TempFileManager()

# ======================================================================================
# TRABAJADORES SEGUROS (HILOS QTHREAD)
# ======================================================================================

class InsertWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, db_path, file_paths):
        super().__init__()
        self.db_path = db_path
        self.file_paths = file_paths

    def run(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            total = len(self.file_paths)
            for i, path in enumerate(self.file_paths, start=1):
                try:
                    base = os.path.basename(path)
                    with open(path, "rb") as f:
                        blob = f.read()
                    cur.execute("INSERT INTO new_employee (name, files) VALUES (?, ?)", (base, blob))
                    self.progress.emit(int(i / total * 100))
                except Exception as e:
                    log_message("WARN", f"Archivo omitido: {path} ({e})")
                    continue
            conn.commit()
            conn.close()
            log_message("INFO", f"Insertados {len(self.file_paths)} archivos correctamente.")
            self.finished.emit(f"Insertados {len(self.file_paths)} archivos.")
        except Exception as e:
            log_message("ERROR", f"Fallo en InsertWorker: {e}")
            self.error.emit(str(e))

##=========================================================================================
##=========================================================================================

class ExtractWorker(QThread):

    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    video_merged = pyqtSignal(str)
    pdf_merged = pyqtSignal(str)
    txt_merged = pyqtSignal(str)
    compress_merged = pyqtSignal(str)

    def __init__(self, db_path, row_ids, out_dir):
        super().__init__()
        self.db_path = db_path
        self.row_ids = row_ids
        self.out_dir = out_dir

    def run(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            total = len(self.row_ids)

            for i, rid in enumerate(self.row_ids, start=1):

                try:

                    cur.execute("SELECT name, files FROM new_employee WHERE id=?", (rid,))
                    rec = cur.fetchone()
                    if not rec:
                        continue

                    name, blob = rec
                    
                    out_path = os.path.join(self.out_dir, name)
                    base, ext = os.path.splitext(out_path)
                    counter = 1

                    while os.path.exists(out_path):
                        out_path = f"{base}({counter}){ext}"
                        counter += 1

                    with open(out_path, "wb") as f:
                        f.write(blob)

                    if not os.path.exists(out_path):
                        temp_file_manager.register(out_path)
                        self.progress.emit(int(i / total * 100))

                        conn.close()
                        msg = f"Archivo|(s) NoExtraído|(s)"
                        log_message("INFO", msg)
                        self.finished.emit(msg)
                        return None

                    else:

                        ext_lower = name.lower()
                        if ext_lower.endswith((".mp4",".mkv",".avi",".flv",".mp3",".wmv",".webm",".wav",
                            ".m4a",".gif", ".mp4v", ".avf", ".divx", ".mpg", ".rmvb", ".wap", ".cda", ".flac")):
                            self.video_merged.emit(out_path)
                        elif ext_lower.endswith(".pdf"):
                            self.pdf_merged.emit(out_path)
                        elif ext_lower.endswith(".txt"):
                            self.txt_merged.emit(out_path)
                        elif ext_lower.endswith((".rar",".zip",".7z")):
                            self.compress_merged.emit(out_path)

                except Exception as e:
                    continue

            conn.close()
            msg = f"Extraídos {len(self.row_ids)} archivos en: {self.out_dir}"
            log_message("INFO", msg)
            self.finished.emit(msg)

        except Exception as e:
            log_message("ERROR", f"Fallo en ExtractWorker: {e}")
            self.error.emit(str(e))

# ======================================================================================
# CLASE PRINCIPAL: MainWindow
# ======================================================================================

@protect_window
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bakup_All_files_PyQt5 v2")
        self.resize(900, 750)

        self.Ico_app = Path.resource_path('Ico\\1.ico')
        self.setWindowIcon(QIcon(self.Ico_app))

        self.db_path = ""
        self.selected_files = []
        self.last_db_dir = ""
        self.ima_copy = ""
        self.cont_vid = 0
        self.video_acction = True
        self.Verificacion_In = True
        self._insert_worker = None
        self._extract_worker = None
        self.init_ui()
        self.apply_styles()
        self.center_on_screen()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        prev = QHBoxLayout()
        prev.setContentsMargins(0,0,0,0)
        central.setLayout(layout)

        self._insert_worker = None
        self._extract_worker = None

        self.playlist = QMediaPlaylist()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setFixedSize(325, 180)
        self.videoWidget.setAspectRatioMode(True)

        # Top row: select files / db / insert
        top_row = QHBoxLayout()
        self.btn_select_files = QPushButton("Seleccionar archivos…")
        self.btn_select_files.clicked.connect(self.select_files)

        self.btn_insert = QPushButton("Insertar a DB")
        self.btn_insert.clicked.connect(self.insert_to_db)

        self.btn_delete = QPushButton("Borrar dato de DB")
        self.btn_delete.clicked.connect(self.deleteRec)

        self.btn_select_db = QPushButton("Crear / Seleccionar DB")
        self.btn_select_db.clicked.connect(self.select_db)

        for b in (self.btn_select_files, self.btn_insert, self.btn_delete, self.btn_select_db):
            top_row.addWidget(b)
        layout.addLayout(top_row)

        # === Combobox y acciones ===
        mid_row = QHBoxLayout()
        mid_row.addWidget(QLabel("Archivos en DB:"))
        self.cb_files = QComboBox()
        self.cb_files.setMinimumWidth(380)
        mid_row.addWidget(self.cb_files)

        self.btn_refresh = QPushButton("Refrescar lista")
        self.btn_refresh.clicked.connect(self.refresh_list)

        self.btn_extract_one = QPushButton("Extraer seleccionado")
        self.btn_extract_one.clicked.connect(self.extract_selected)

        self.btn_extract_all = QPushButton("Extraer todos")
        self.btn_extract_all.clicked.connect(self.extract_all)

        for b in (self.btn_refresh, self.btn_extract_one, self.btn_extract_all):
            mid_row.addWidget(b)

        layout.addLayout(mid_row)

        # === Log ===
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Mensajes y registros aparecerán aquí...")
        layout.addWidget(self.log, stretch=1)

        # === Vista previa ===
        preview_frame = QFrame()
        preview_layout = QHBoxLayout()
        preview_frame.setLayout(preview_layout)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(250, 180)
        self.preview_label.setStyleSheet("background:#ffffff; border:1px solid #dfeaf6;")
        preview_layout.addWidget(self.preview_label)
        #preview_layout.addStretch()

        # Conectar el clic del label al método de reproducción
        self.preview_label.mousePressEvent = lambda event: self.Vista_Previa_Image(event)
        prev.addWidget(preview_frame)

        self.previousframe = QPushButton()
        self.previousframe.setStyleSheet('QPushButton {background-color: #80ff80; border: 1px; border-style:outset; \
            border-width:1px; border-radius:10px; border-color:beige; color: #ff0000; font:bold 14px; \
            min-width:1em; padding:6px;}  QPushButton:hover {background-color: #45a049;}')
        self.previousframe.setFixedWidth(100)
        self.previousframe.setFixedHeight(180)
        self.previousframe.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.previousframe.setToolTip('Rep. Play | Pausa')
        self.previousframe.clicked.connect(lambda: Play_All_Videos.MediaPause_Vid(self))

        # Create the "next frame" button
        self.nextframe = QPushButton()
        self.nextframe.setStyleSheet('QPushButton {background-color: #4d9999; border: 1px; border-style:outset; \
            border-width:1px; border-radius:10px; border-color:beige; color: #ff0000; font:bold 14px; min-width:1em; \
            padding:6px;}  QPushButton:hover {background-color: #0000ff;}')
        self.nextframe.setFixedWidth(100)
        self.nextframe.setFixedHeight(180)
        self.nextframe.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.nextframe.setToolTip('Rep. Stop')
        self.nextframe.clicked.connect(lambda: Play_All_Videos.stop_clicked(self))

        prev.addWidget(self.previousframe)
        prev.addWidget(self.nextframe)
        prev.addWidget(self.videoWidget)

        # Bottom row
        bottom_row = QHBoxLayout()
        self.btn_clean = QPushButton("Limpiar log")
        self.btn_clean.clicked.connect(self.clean_log)
        bottom_row.addWidget(self.btn_clean)

        # small spacer
        bottom_row.addStretch()

        # progress / indicator label for pulses
        self.indicator = QLabel("●")
        self.indicator.setFixedWidth(20)
        self.indicator.setStyleSheet("color: #2b8fef; font-weight: bold;")
        preview_effect = QGraphicsOpacityEffect(self.indicator)
        preview_effect.setOpacity(1.0)
        self.indicator.setGraphicsEffect(preview_effect)
        self.indicator_opacity_effect = preview_effect  # keep reference
        bottom_row.addWidget(self.indicator)

        layout.addLayout(prev)
        layout.addLayout(bottom_row)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.update_status("Listo. Selecciona o crea la base de datos.", write_log=False)

        # Connect combo change to preview attempt
        self.cb_files.currentIndexChanged.connect(self.on_combo_change)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.videoWidget.installEventFilter(self)

        # Esta variable guardará la referencia a la ventana del reproductor
        self.player_window = None

        # === Temporizador principal ===
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: MainWindow.media_P_state(self))
        self.timer.start(1000)  # 10 segundos
        monitor_timer(self.timer)
        log_message("INFO", "Mensaje de estado")
        # self.pulse_indicator() # <-- Si se desea que el pulso, este ciempre activo Descomentar.-

# ======================================================================================
# CONTROL DE ## Exit (Clouse App) Cerrar la Aplicación
# ======================================================================================
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: ## Key Board (Teclado - Tecla Escape (ESC))
            sys.exit()

    ## Metodo para Hacer Full Screen el Widget del Video (QMediaPlayer())
    ## Metodo (Original), con (MouseButtonDblClick)
    def eventFilter(self, obj, event):

        if event.type() == QEvent.MouseButtonPress:

            self.video_acction = True
            self.mediaPlayer.stop()
            self.playlist.clear()
            self.mediaPlayer.setMedia(QMediaContent())

            self.cont_vid += 1

            bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath( os.path.dirname(__file__) ) )
            dir_gifs = os.path.join(bundle_dir, "sticker",)

            self.ima_copy = os.listdir(dir_gifs)
            
            print((dir_gifs + self.ima_copy[self.cont_vid]))
            file_path = f'{dir_gifs}\\{self.ima_copy[self.cont_vid]}'
            Play_All_Videos.display_video(self, file_path)

        return False

    ##------------------------------------------
    # -> Imagen en Bites desde la Base de Datos
    ##------------------------------------------
    def Vista_Previa_Image(self, event):
        global name

        try:

            rid = self.cb_files.currentData()

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT name, files FROM new_employee WHERE id=?", (rid,))
            rec = cur.fetchone()
            conn.close()

            if not rec:
                self.preview_label.clear()
                self.preview_label.setText("No preview")
                return

            name, blob = rec
            ext_lower = name.lower()

            fpath, fname = os.path.split(name)
            name, ext = os.path.splitext(name)
            print(ext)

            if any(ext_lower.endswith(ext) for ext in (".rar",".zip",".7z")):
                print(f"{ext}")

                message = QMessageBox.question(self, 'Pregunta?', f'Deseas Inspeccionar el Archivo Comprimido (*.{ext})?', QMessageBox.Yes | QMessageBox.No)

                if message == QMessageBox.Yes:
                    webbrowser.open_new(self.output_path)

            elif any(ext_lower.endswith(ext) for ext in (".jpg",".png",".jpeg",".bmp",".tiff")):
                print(f"{ext}")

                try:

                    #Imagen en Bites desde la Base de Datos
                    imagen_pil = Image.open(io.BytesIO(blob))
                    #Transformamos dicha Imagen para CV2
                    image = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
                    #Extraemos el Nombre guardado para la Ventana Emergente de Previsualización de CV2
                    x = f'Image:  {name}.-'
                    #Hacemos la Ventana de CV2 Redimencionale
                    cv2.namedWindow(f"{x}",cv2.WINDOW_NORMAL)
                    # Para Ver la Imagen dentr de la Ventana Emergente Image de CV2
                    cv2.imshow(f"{x}", image)
                    #Cerramos la Ventana
                    cv2.waitKey(0)

                except Exception as e:
                    print('Error 8')
                    print(e)

            elif any(ext_lower.endswith(ext) for ext in (".docx")):
                print(f"{ext}")
                
                message1 = QMessageBox.question(self, 'Pregunta?', f'Deseas Inspeccionar el Archivo *..{ext}?', QMessageBox.Yes | QMessageBox.No)

                if message1 == QMessageBox.Yes:
                    webbrowser.open_new(self.output_path)

            elif any(ext_lower.endswith(ext) for ext in (".xlsx")):
                print(f"{ext}")
                
                message2 = QMessageBox.question(self, 'Pregunta?', f'Deseas Inspeccionar el Archivo *..{ext}?', QMessageBox.Yes | QMessageBox.No)

                if message2 == QMessageBox.Yes:
                    webbrowser.open_new(self.output_path)

            elif any(ext_lower.endswith(ext) for ext in (".pdf")):
                print(f"{ext}")
                
                message2 = QMessageBox.question(self, 'Pregunta?', f'Deseas Inspeccionar el Archivo *.{ext}?', QMessageBox.Yes | QMessageBox.No)

                if message2 == QMessageBox.Yes:
                    open_pdf_with_sumatra(self, self.output_path)

            elif any(ext_lower.endswith(ext) for ext in (".txt")):
                print(f"{ext}")
                
                message2 = QMessageBox.question(self, 'Pregunta?', f'Deseas Inspeccionar el Archivo *.{ext}?', QMessageBox.Yes | QMessageBox.No)

                if message2 == QMessageBox.Yes:
                    TXT_Lec.Frame_TXT_Lec(self, self.output_path)

            elif any(ext_lower.endswith(ext) for ext in (
                ".mp4",".mkv",".avi",".flv",".mp3",".wmv",".webm",".wav",".m4a",".gif", ".mp4v", 
                ".avf", ".divx", ".mpg", ".rmvb", ".wap", ".cda", ".flac")):
                print(f"{ext}")

                Play_All_Videos2.display_video2(self, self.output_path)

        finally:
            event.accept()

# ======================================================================================
# CONTROL DE REPRODUCCIÓN Y TEMPORIZADOR
# ======================================================================================

    def media_P_state(self):
        """Controla el estado de reproducción de videos y limpia temporales al detener."""
        try:
            if not self.Verificacion_In:
                return
            if self.video_acction and self.mediaPlayer.state() == QMediaPlayer.StoppedState:
                self.cont_vid += 1
                self.playlist.clear()
                self.play_video_prev()
            elif not self.video_acction and self.mediaPlayer.state() == QMediaPlayer.StoppedState:
                self.video_acction = True
                self.mediaPlayer.stop()
                self.playlist.clear()
                self.mediaPlayer.setMedia(QMediaContent())
                time.sleep(0.12)
                
                self.cont_vid = 0
                self.play_video_prev()
        except Exception as e:
            log_message("ERROR", f"media_P_state: {e}")

    def play_video_prev(self):

        ## Forma 1 - para localizar la Carpeta ('sticker'), dentro de la App. en el Dir Raiz
        bundle_dir = getattr(sys, "_MEIPASS", os.path.abspath( os.path.dirname(__file__) ) )
        dir_gifs = os.path.join(bundle_dir, "sticker",)


        if not os.path.exists(dir_gifs):                                
            print('No Existo...')
            
        else:

            self.ima_copy = os.listdir(dir_gifs)
            if self.cont_vid == len(self.ima_copy):

                self.cont_vid = 0
                MainWindow.play_video_prev(self)

            elif self.cont_vid >= len(self.ima_copy):

                self.cont_vid = 0
                MainWindow.play_video_prev(self)

            else:

                print((dir_gifs+self.ima_copy[self.cont_vid]))
                file_path = f'{dir_gifs}\\{self.ima_copy[self.cont_vid]}'
                Play_All_Videos.display_video(self, file_path)

    # -------------------------
    # Visual / style helpers
    # -------------------------
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background: #f0f4f7; }
            QTextEdit { background: #ffffff; border: 1px solid #bfcbd9; border-radius:4px; }
            QComboBox { background:#fff; border:1px solid #b0c7e0; padding:3px; border-radius:4px; }
            QPushButton {
                background-color: #e7f3fb;
                border: 1px solid #9ec8ef;
                border-radius: 8px;
                padding:6px 10px;
                font-weight:bold;
                color:#003366;
            }
            QPushButton:hover {
                background-color: #d2ecff;
                border: 1px solid #3b95e0;
            }
            QPushButton:pressed {
                background-color: #a8d4f8;
            }
        """)
        pal = self.palette()
        pal.setColor(QPalette.WindowText, QColor("#003366"))
        self.setPalette(pal)

    def update_status(self, text, write_log=True):
        # show message and append in log
        self.status.showMessage(text, 7000)
        if write_log:
            self.log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}")
            # also write to Resume_Data_2.txt for info messages (we'll write to Resume_Data.txt for operations)
            self.append_resume2(text)

    def pulse_indicator(self):
        # subtle pulse on self.indicator using opacity animation
        anim = QPropertyAnimation(self.indicator_opacity_effect, b"opacity")
        anim.setDuration(600)
        anim.setStartValue(0.2)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.setLoopCount(2)
        anim.start()
        # keep reference to avoid GC
        self._last_indicator_anim = anim

    def clean_log(self):
        self.log.clear()
        self.update_status("Caja de texto limpiada.", write_log=False)

    # -------------------------
    # DB / File actions
    # -------------------------
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleccionar archivos", os.path.expanduser("~"))
        if files:
            self.selected_files = files
            self.log.append(f"[{len(files)}] archivos seleccionados:")
            for f in files:
                self.log.append(f"  • {f}")
            self.update_status(f"{len(files)} archivos seleccionados. Presiona 'Insertar a DB' para guardarlos.")
            # attempt small preview for first selected if image
            self.try_preview_file(files[0])

# ======================================================================================
# CARGA / SELECCIÓN DE BASE DE DATOS
# ======================================================================================

    def select_db(self):
        """Selecciona o crea la base de datos SQLite y reactiva el temporizador con seguridad."""
        try:
            self.stop_thread()
            self.mediaPlayer.stop()

            folder = QFileDialog.getExistingDirectory(
                self, 
                "Seleccionar carpeta para DB (se creará DB/Data_Base)", 
                os.path.expanduser("~")
            )
            if not folder:
                return

            db_dir = os.path.join(folder, "DB", "Data_Base")
            safe_mkdir(db_dir)
            db_file = os.path.join(db_dir, "SQLite_Python.db")
            self.db_path = db_file
            self.last_db_dir = db_dir

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(DB_TABLE_SQL)
            conn.commit()
            conn.close()

            self.update_status(f"DB lista: {self.db_path}")
            self.ensure_resume_files()
            self.refresh_list()

            self.previousframe.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.playlist.clear()
            self.cont_vid = 0
            self.Verificacion_In = True

            self.btn_select_db.hide()

        except Exception as e:
            QMessageBox.critical(self, "Error al abrir DB", str(e))
            self.update_status("❌ Error al inicializar la base de datos.")
            log_message("ERROR", f"select_db: {e}")

        else:

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id FROM new_employee ORDER BY id DESC") # ORDER BY id ASC
            rows = cur.fetchall()
            conn.close()
            ids = [r[0] for r in rows]
            print(ids)

            if ids == []:

                self.mediaPlayer.stop()
                self.video_acction = False
                print("Bacio...")
                self.in_first_data()
                self.refresh_list()

        finally:
            if hasattr(self, "timer") and not self.timer.isActive():
                self.timer.start(1000)
            log_message("INFO", "⏱️ Temporizador reactivado correctamente tras select_db().")

    def in_first_data(self):

        base = "Sección para Archivos"
        blob = ""

        con=sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute("INSERT INTO new_employee (name, files) VALUES (?, ?)", (base, blob))
        con.commit()
        con.close()


    def ensure_resume_files(self):
        if not self.last_db_dir:
            return
        resume1 = os.path.join(self.last_db_dir, "Resume_Data.txt")
        resume2 = os.path.join(self.last_db_dir, "Resume_Data_2.txt")

        # create if not exists
        for p in (resume1, resume2):
            if not os.path.exists(p):
                append_to_file(p, f"=== Created {os.path.basename(p)} at {datetime.now().isoformat()} ===")
        
        # write header entry indicating UI started
        self.append_resume2("Interfaz iniciada y archivos resume verificados.")

    def append_resume(self, text):
        """Write to Resume_Data.txt (operational logs)"""
        if not self.last_db_dir:
            return

        p = os.path.join(self.last_db_dir, "Resume_Data.txt")
        append_to_file(p, f"[{datetime.now().isoformat()}] {text}")

    def append_resume2(self, text):
        """Write to Resume_Data_2.txt (system / info logs)"""
        if not self.last_db_dir:
            return

        p = os.path.join(self.last_db_dir, "Resume_Data_2.txt")
        append_to_file(p, f"[{datetime.now().isoformat()}] {text}")

    def insert_to_db(self):
        self.stop_thread()

        if not self.db_path:
            QMessageBox.warning(self, "DB no seleccionada", "Primero crea o selecciona la base de datos.")
            return

        if not self.selected_files:
            QMessageBox.warning(self, "Sin archivos", "No has seleccionado archivos para insertar.")
            return

        self.Verificacion_In = False
        self.mediaPlayer.stop()
        self.timer.stop()
        self.playlist.clear()

        self.update_status("Insertando archivos en la DB...")
        self.append_resume(f"Start insert: {len(self.selected_files)} files")
        # start worker
        self._insert_worker = InsertWorker(self.db_path, self.selected_files)
        self._insert_worker.finished.connect(self.on_insert_finished)
        self._insert_worker.error.connect(self.on_worker_error)
        self._insert_worker.progress.connect(self.on_progress)
        self._insert_worker.start()

        self.Verificacion_In = True
        self.timer.start()

    def on_progress(self, pct):
        # optional: show progress in status briefly
        self.status.showMessage(f"Progreso: {pct}%")

    def on_insert_finished(self, msg):
        self.log.append("[INSERT] " + msg)
        self.append_resume(msg)
        self.append_resume2("Insert finished: " + msg)
        self.update_status(msg)
        self.selected_files = []
        self.refresh_list()
        self.pulse_indicator()

    def on_worker_error(self, err):
        self.log.append("[ERROR] " + err)
        self.append_resume2("ERROR: " + err)
        QMessageBox.critical(self, "Error", err)
        self.update_status("Error en operación.")
        self.pulse_indicator()

    def refresh_list(self):

        self.cb_files.clear()

        if not self.db_path or not os.path.exists(self.db_path):
            self.update_status("DB no encontrada. Selecciona/crea la DB.", write_log=False)
            return

        try:

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM new_employee ORDER BY id ASC")
            rows = cur.fetchall()
            conn.close()

            for r in rows:
                self.cb_files.addItem(f"{r[0]} - {r[1]}", r[0])

            self.update_status(f"Cargados {len(rows)} registros desde la DB.")
            # attempt preview of first row (non-blocking)

            if rows:
                first_id = rows[0][0]
                self.try_preview_db_row(first_id)

        except Exception as e:
            self.log.append("[ERROR] " + str(e))
            self.update_status("Error al leer DB.")

    def extract_selected(self):
        if not self.db_path:
            QMessageBox.warning(self, "DB no seleccionada", "Primero crea o selecciona la base de datos.")
            return

        idx = self.cb_files.currentIndex()
        if idx < 0:
            QMessageBox.information(self, "Nada seleccionado", "Selecciona un archivo en el combo.")
            return

        row_id = self.cb_files.currentData()
        out_dir = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta destino para extracción", os.path.expanduser("~"))
        if not out_dir:
            return

        self.update_status("Extrayendo archivo...")
        self.append_resume(f"Start extract: id {row_id}")
        self._extract_worker = ExtractWorker(self.db_path, [row_id], out_dir)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.start()

    def extract_all(self):
        if not self.db_path:
            QMessageBox.warning(self, "DB no seleccionada", "Primero crea o selecciona la base de datos.")
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta destino para extracción", os.path.expanduser("~"))
        if not out_dir:
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM new_employee ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        ids = [r[0] for r in rows]

        if not ids:
            QMessageBox.information(self, "DB vacía", "No hay registros para extraer.")
            return

        self.update_status("Extrayendo todos los archivos...")
        self.append_resume(f"Start extract ALL: count {len(ids)}")
        self._extract_worker = ExtractWorker(self.db_path, ids, out_dir)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.start()

    def on_extract_finished(self, msg):
        self.log.append("[EXTRACT] " + msg)
        self.append_resume(msg)
        self.append_resume2("Extract finished: " + msg)
        self.update_status(msg)
        self.pulse_indicator()

        QMessageBox.information(self, "Exito", "Archivo(´s) Extrraido(´s), Exitosamente.")

    # -------------------------
    # Borra Dato Selecciónado - Pero deja un Bujero
    # -------------------------
    def deleteRec(self):

        message = QMessageBox.question(self, 'Pregunta?', 'Deseas Borrar de la BD, este Dato?', QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:

            db_path = os.path.isfile(self.db_path)
            if db_path == True:

                row_id = self.cb_files.currentData()
        
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT name, files FROM new_employee WHERE id=?", (row_id,))
                rec = cur.fetchone()
                conn.close()

                name, blob = rec

                con=sqlite3.connect(self.db_path)
                cur=con.cursor()
                cur.execute("DELETE FROM new_employee WHERE name=?", (name,))
                con.commit()
                con.close

                msg = f"Dato Seleccionado Borrado con Exito. {name}"
                self.log.append("[INSERT] " + msg)
                log_message("INFO", f"{msg}")
                self.refresh_list()

            if db_path == False:
                self.update_status("❌ Error al inicializar la base de datos.")
                QMessageBox.warning(self, "❌ Error", "No hay base de datos, con que Trabajar.")
                return

        else:
            pass

    # -------------------------
    # Preview helpers
    # -------------------------
    def try_preview_file(self, path):

        # If image: show scaled preview. If not image, show icon or clear.
        try:

            img = Image.open(path)
            img.thumbnail((160, 160))
            b = img.convert("RGBA").tobytes("raw", "RGBA")
            qimg = QImage(b, img.width, img.height, QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pix)

        except (UnidentifiedImageError, OSError):
            # not an image or failed — clear preview
            self.preview_label.clear()
            self.preview_label.setText("No preview")

        except Exception as e:
            self.preview_label.clear()
            self.preview_label.setText("No preview")

# -----------------------------------------------------------------------------
# Coloca las Miniaturas, de las Extenciónes Correspondientes
# -----------------------------------------------------------------------------
    def extent_imgs(self, name_file):

        fpath, fname = os.path.split(name_file)
        name, ext = os.path.splitext(name_file)

        if fname.endswith(f"{ext}"):
            filename = ext.replace('.', '').upper()
            print(filename)

            for dirpath, dirnames, filenames in os.walk(directory):
                if f'{filename}.png' in filenames:

                    filename_P = dirpath+f'{filename}.png'
                    self.filename = str(filename_P)

                    self.preview_label.setScaledContents(True)
                    pixmap = QPixmap(self.filename).scaledToWidth(1000)
                    pixmap = pixmap.scaledToHeight(500)

                    self.preview_label.setPixmap(pixmap)

                else:

                    filename_P = dirpath+'Default.png'
                    self.filename = str(filename_P)

                    self.preview_label.setScaledContents(True)
                    pixmap = QPixmap(self.filename).scaledToWidth(1000)
                    pixmap = pixmap.scaledToHeight(500)

                    self.preview_label.setPixmap(pixmap)

        return

# -----------------------------------------------------------------------------
# Modificar try_preview_db_row para usar directorio temporal
# -----------------------------------------------------------------------------
    def try_preview_db_row(self, row_id):

        """El Primer Item dentro de la Listia, Sera solamente, una Instrucción"""
        if self.cb_files.currentIndex() == 0:
            print("⚠️ Primero selecciona una opción válida.")
            return

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name, files FROM new_employee WHERE id=?", (row_id,))
        rec = cur.fetchone()
        conn.close()

        if not rec:
            self.preview_label.clear()
            self.preview_label.setText("No preview")
            return

        name, blob = rec
        self.extent_imgs(name)

        try:
            ext_lower = name.lower()
            if any(ext_lower.endswith(ext) for ext in (
                ".mp4",".mkv",".avi",".flv",".mp3",".wmv",".webm",".wav",".m4a",".gif", ".mp4v", 
                ".avf", ".divx", ".mpg", ".rmvb", ".wap", ".cda", ".flac")):

                self.mediaPlayer.stop()
                self.video_acction = False
                tmp_dir = tempfile.mkdtemp(prefix="bakup_preview_")
                self.output_path = os.path.join(tmp_dir, name)
                temp_file_manager.register(self.output_path)
                self.playlist.clear()
                MainWindow.extract_selected2(self, name, self.output_path, tmp_dir)

            elif any(ext_lower.endswith(ext) for ext in (".jpg",".png",".jpeg",".bmp",".tiff")):

                imagen_pil = Image.open(io.BytesIO(blob))
                image = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_BGR2RGB)
                frame = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
                self.preview_label.setScaledContents(True)
                self.preview_label.setPixmap(QPixmap.fromImage(image))

            elif any(ext_lower.endswith(ext) for ext in (".pdf")):

                self.mediaPlayer.stop()
                self.video_acction = False
                tmp_dir = tempfile.mkdtemp(prefix="bakup_preview_")
                self.output_path = os.path.join(tmp_dir, name)
                temp_file_manager.register(self.output_path)
                self.playlist.clear()
                MainWindow.extract_selected3(self, name, self.output_path, tmp_dir)

            elif any(ext_lower.endswith(ext) for ext in (".txt")):

                self.mediaPlayer.stop()
                self.video_acction = False
                tmp_dir = tempfile.mkdtemp(prefix="bakup_preview_")
                self.output_path = os.path.join(tmp_dir, name)
                temp_file_manager.register(self.output_path)
                self.playlist.clear()
                MainWindow.extract_selected4(self, name, self.output_path, tmp_dir)

            else:

                self.mediaPlayer.stop()
                self.video_acction = False
                tmp_dir = tempfile.mkdtemp(prefix="bakup_preview_")
                self.output_path = os.path.join(tmp_dir, name)
                temp_file_manager.register(self.output_path)
                self.playlist.clear()
                MainWindow.extract_selected5(self, name, self.output_path, tmp_dir)

        except Exception as e:
            self.preview_label.clear()
            self.preview_label.setText("No preview")

    def extract_selected2(self, name, output_path, path):

        row_id = self.cb_files.currentData()

        self.update_status("Extrayendo archivo...")
        self.append_resume(f"Start extract: id {row_id}")
        self._extract_worker = ExtractWorker(self.db_path, [row_id], path)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.video_merged.connect(lambda: Play_All_Videos2.display_video2(self, output_path))
        self._extract_worker.start()

    def extract_selected3(self, name, output_path, path):

        row_id = self.cb_files.currentData()

        self.update_status("Extrayendo archivo...")
        self.append_resume(f"Start extract: id {row_id}")
        self._extract_worker = ExtractWorker(self.db_path, [row_id], path)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.pdf_merged.connect(lambda: open_pdf_with_sumatra(self, output_path))
        self._extract_worker.start()

    def extract_selected4(self, name, output_path, path):

        row_id = self.cb_files.currentData()

        self.update_status("Extrayendo archivo...")
        self.append_resume(f"Start extract: id {row_id}")
        self._extract_worker = ExtractWorker(self.db_path, [row_id], path)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.txt_merged.connect(lambda: TXT_Lec.Frame_TXT_Lec(self, output_path))
        self._extract_worker.start()

    def extract_selected5(self, name, output_path, path):

        row_id = self.cb_files.currentData()

        self.update_status("Extrayendo archivo...")
        self.append_resume(f"Start extract: id {row_id}")
        self._extract_worker = ExtractWorker(self.db_path, [row_id], path)
        self._extract_worker.finished.connect(self.on_extract_finished)
        self._extract_worker.error.connect(self.on_worker_error)
        self._extract_worker.progress.connect(self.on_progress)
        self._extract_worker.compress_merged.connect(lambda: Filesunpack.unpackFiles(self, output_path))
        self._extract_worker.start()

    def on_combo_change(self, index):
        # attempt to preview the selected db entry
        if index < 0:
            return
        row_id = self.cb_files.itemData(index)
        if row_id is not None:
            # non-blocking preview is fine as db reads are small; if heavy, put into a worker
            self.try_preview_db_row(row_id)

    def stop_thread(self):
        """Detiene el hilo si está corriendo"""
        if self._insert_worker and self._insert_worker.isRunning():
            self._insert_worker.terminate()
            self._insert_worker.wait()
            self.label.setText("⛔ Hilo detenido.")

        elif self._extract_worker and self._extract_worker.isRunning():
            self._extract_worker.terminate()
            self._extract_worker.wait()
            self.label.setText("⛔ Hilo detenido.")

        else:
            print("ℹ️ No hay hilo activo.")

# ======================================================================================
# CIERRE SEGURO DE LA APLICACIÓN
# ======================================================================================

    def closeEvent(self, event):
        """Intercepta el cierre de la ventana para detener hilos y limpiar todo con seguridad."""
        try:
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()

            if hasattr(self, "mediaPlayer"):
                self.mediaPlayer.stop()
                self.playlist.clear()

            if hasattr(self, "_insert_worker") and self._insert_worker and self._insert_worker.isRunning():
                self._insert_worker.terminate()
                self._insert_worker.wait()

            if hasattr(self, "_extract_worker") and self._extract_worker and self._extract_worker.isRunning():
                self._extract_worker.terminate()
                self._extract_worker.wait()

            temp_file_manager.delete_all()
            log_message("INFO", "💡 Cierre seguro completado correctamente.")

        except Exception as e:
            log_message("ERROR", f"Error en cierre: {e}")

        finally:

            time.sleep(0.12)

            if hasattr(self, "output_path"):
                ok = temp_file_manager.delete_with_retries(self.output_path)
                if not ok:
                    log_message("INFO", f"⚠️ No se pudo borrar temporal: {self.output_path}")

            event.accept()

# -----------------------------------------------------------------------------
# Play_All_Videos For Demo
# -----------------------------------------------------------------------------
class Play_All_Videos(MainWindow):

    def __init__(self):
        super().__init__()

    def display_video(self, file_path):

        self.playlist.clear()

        try:

            # Control de reproducción de video de Qt.
            self.palylist = QMediaPlaylist()
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(file_path)))

            self.mediaPlayer.setPlaylist(self.playlist)
            self.mediaPlayer.playlist().setCurrentIndex(0)
            self.mediaPlayer.play()

        except Exception as e:
            print(e)

            Message_Box.dialog_critical(self, str(f'{e}'))
            Acctions_App.concluidas_las_tareas(self)

    def MediaPause_Vid(self):

        try:
            if self.ima_copy == [] or self.ima_copy == "":
                pass

            else:

                if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                    self.previousframe.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))                    
                    self.pause = True
                    self.mediaPlayer.pause()
                    self.timer.stop()

                else:

                    self.previousframe.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                    self.pause = False
                    self.mediaPlayer.play()
                    self.timer.start()

        except Exception as e:
            print(e)

    def stop_clicked(self):
        if not self.ima_copy:
            return
        self.previousframe.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        try:
            self.mediaPlayer.stop()
            self.playlist.clear()
            self.mediaPlayer.setMedia(QMediaContent())
        except Exception as e:
            print("stop_clicked:", e)
        self.timer.stop()

##=========================================================================================================
##=========================================================================================================

class TXT_Lec(MainWindow):

    def __init__(self):
        super().__init__()

    def Frame_TXT_Lec(self, output_path):

        dialog = QDialog(self)
        dialog.setWindowTitle("Contenido del Archivo")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.center_on_screen()

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        fpath, fname = os.path.split(output_path)
        label = QLabel(f'Nombre del Texto: -> {fname}')
        layout.addWidget(label)

        # Create Font Size, Font Bold, Font Wieight, Font PonintSize
        self.font_txt = QtGui.QFont()
        self.font_txt.setPointSize(20)
        self.font_txt.setBold(True)
        self.font_txt.setWeight(50)

        self.editor = QPlainTextEdit()
        self.editor.setFont(self.font_txt)
        layout.addWidget(self.editor)

        try:

            try:

                with open(output_path, 'r') as f:
                    text = f.read()

                    print(text)
                    self.editor.setPlainText(text)

            except Exception as e:
                print(e)
                log_message("WARN", f"Intento fallido al inniciar lectura en {fname}:\n {e}")

        except Exception as e:
            print(e)
            #QMessageBox.critical(self, "Error", str(e))
            log_message("WARN", f"Intento fallido al inniciar lectura en {fname}:\n {e}")

            try:

                with open(output_path, 'r', encoding="utf-8") as f:
                    text = f.read()

                    print(text)
                    self.editor.setPlainText(text)

            except Exception as e:
                print(e)
                log_message("WARN", f"Intento fallido al inniciar lectura en {fname}:\n {e}")

        dialog.exec_()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, 300, 200)

##=========================================================================================================
##=========================================================================================================

class Filesunpack(MainWindow):

    def __init__(self):
        super().__init__()

    def unpackFiles(self, output_path):

        fpath, fname = os.path.split(output_path)
        name, ext = os.path.splitext(output_path)

        filename = ""
        results = []
        names = []
        fileName = ext.replace('.', '')

        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:

                if f'{fileName.upper()}.png' in filename:
                    fileName = f'{fileName.upper()}.png'
                    
                    if fileName.endswith(".png"):

                        path = dirpath.replace('\\', '/')
                        dir_path = path+'/'+filename

                        fpath, fname = os.path.split(f'{dir_path}')
                        self.filename = fpath+'/'+filename
                        
                        self.preview_label.setScaledContents(True)
                        pixmap = QPixmap(self.filename).scaledToWidth(1000)
                        pixmap = pixmap.scaledToHeight(500)

                        self.preview_label.setPixmap(pixmap)

                elif f'{fileName.lower()}.png' in filename:
                    fileName = f'{fileName.lower()}.png'

                    if fileName.endswith(".png"):

                        path = dirpath.replace('\\', '/')
                        dir_path = path+'/'+filename

                        fpath, fname = os.path.split(f'{dir_path}')
                        self.filename = fpath+'/'+filename

                        self.preview_label.setScaledContents(True)
                        pixmap = QPixmap(self.filename).scaledToWidth(1000)
                        pixmap = pixmap.scaledToHeight(500)

                        self.preview_label.setPixmap(pixmap)

                else:
                    image = 'Default.png'

                    if image in filename:
                        filename_P = directory+image
                        self.filename = str(filename_P)

                        self.preview_label.setScaledContents(True)
                        pixmap = QPixmap(self.filename).scaledToWidth(1000)
                        pixmap = pixmap.scaledToHeight(500)

                        self.preview_label.setPixmap(pixmap)

# ======================================================================================
# FUNCIÓN PRINCIPAL PARA VER LA PREVISUALIZACIÓN DE LOS VIDEOS
# ======================================================================================
class Play_All_Videos2(MainWindow):

    def __init__(self):
        super().__init__()

    def display_video2(self, file_path):

        message = QMessageBox.question(self, 'Pregunta?', 'Ver una "PREVISUALIZACIÓN"?', QMessageBox.Yes | QMessageBox.No)
        if message == QMessageBox.Yes:

            """Abre el diálogo para seleccionar un archivo de video."""
            # Filtro para tipos de video comunes

            if file_path:
                # Si se seleccionó un archivo, creamos la ventana emergente
                Play_All_Videos2.show_player_window(self, file_path)

        else:
            pass

    def show_player_window(self, video_path):
        """Crea y muestra la ventana emergente con el reproductor de video."""
        # Si ya hay una ventana abierta, la cerramos para evitar múltiples instancias
        if self.player_window:
            self.player_window.close()

        # Creamos una nueva QMainWindow para la ventana emergente
        self.player_window = QMainWindow()
        self.player_window.setWindowTitle("Reproductor de Video")
        self.Ico_app = Path.resource_path('Ico\\1.ico')
        self.player_window.setWindowIcon(QIcon(self.Ico_app))
        #self.player_window.setGeometry(300, 300, 800, 600) # Tamaño inicial de la ventana del video
        
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 800, 600
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.player_window.setGeometry(x, y, w, h)

        # Creamos una instancia de TU widget de video
        player_widget = VideoPlayerWidget()

        # Configuramos la instancia del widget para que se comporte como una ventana independiente
        # Conectamos su señal de cierre a la función que cierra la ventana emergente
        player_widget.request_close.connect(lambda: Play_All_Videos2.close_player_window(self, video_path))

        # Cargamos el video en el widget
        player_widget.open_file(video_path)

        # Establecemos el widget de video como el widget central de la ventana emergente
        self.player_window.setCentralWidget(player_widget)

        # Mostramos la ventana emergente
        self.player_window.show()

    def close_player_window(self, file_path):
        """Cierra la ventana del reproductor."""
        if self.player_window:
            self.player_window.close()
            self.player_window = None
            time.sleep(0.12)

            if hasattr(self, "output_path"):
                ok = temp_file_manager.delete_with_retries(self.output_path)
                if not ok:
                    print("❌ Error - No se pudo borrar temporal:", self.output_path)
            
# ======================================================================================
# FUNCIÓN PRINCIPAL
# ======================================================================================

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(temp_file_manager.delete_all)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

##=========================================================================================
##=========================================================================================


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    main()

##=========================================================================================
##=========================================================================================