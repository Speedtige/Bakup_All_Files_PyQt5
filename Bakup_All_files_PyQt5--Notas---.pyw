
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Desarrollador: Cristian M. Veliz Cano
Proyecto: Bakup_All_files_PyQt5
Versión: v1.2 Stable
Compatibilidad: Python 3.8.3 / PyQt5 / Windows 7+
Descripción:
  Interfaz PyQt5 para insertar y extraer archivos de una DB SQLite.
  Incluye limpieza segura de hilos, protección de temporizadores y registro dual (print + log).
"""

import os, sys, io, time, sqlite3, shutil, tempfile, atexit, traceback
from datetime import datetime
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import numpy as np, cv2, imutils, subprocess, zipfile, rarfile, py7zr, webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QComboBox, QLabel,
    QStatusBar, QFrame, QStyle, QDialog, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QUrl
from PyQt5.QtGui import QPixmap, QImage, QColor, QPalette
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QGraphicsOpacityEffect

from stability_patch_v1 import protect_window, monitor_timer, log_message

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
                temp_file_manager.register(out_path)
                self.progress.emit(int(i / total * 100))

                ext_lower = name.lower()
                if ext_lower.endswith((".mp4",".mkv",".avi",".flv",".mp3",".wmv",".webm",".wav",".m4a",".gif",".divx",".mpg",".rmvb",".flac")):
                    self.video_merged.emit(out_path)
                elif ext_lower.endswith(".pdf"):
                    self.pdf_merged.emit(out_path)
                elif ext_lower.endswith(".txt"):
                    self.txt_merged.emit(out_path)
                elif ext_lower.endswith((".rar",".zip",".7z")):
                    self.compress_merged.emit(out_path)

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
        self.setWindowTitle("Bakup_All_files_PyQt5 — Stable Edition")
        self.resize(900, 750)
        self.db_path = ""
        self.selected_files = []
        self.last_db_dir = ""
        self._insert_worker = None
        self._extract_worker = None
        self.Verificacion_In = True
        self.cont_vid = 0
        self.video_acction = True

        self.init_ui()
        self.apply_styles()
        self.center_on_screen()

        log_message("INFO", "Interfaz inicializada correctamente.")

    # ----------------------------------------------------------------------------------
    # CONFIGURACIÓN DE INTERFAZ
    # ----------------------------------------------------------------------------------
    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = self.width(), self.height()
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # === Barra superior ===
        top_row = QHBoxLayout()
        self.btn_select_files = QPushButton("Seleccionar archivos…")
        self.btn_select_files.clicked.connect(self.select_files)
        self.btn_select_db = QPushButton("Crear / Seleccionar DB")
        self.btn_select_db.clicked.connect(self.select_db)
        self.btn_insert = QPushButton("Insertar a DB")
        self.btn_insert.clicked.connect(self.insert_to_db)

        for b in (self.btn_select_files, self.btn_select_db, self.btn_insert):
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
        self.log.setPlaceholderText("Mensajes y registros aparecerán aquí…")
        layout.addWidget(self.log, stretch=1)

        # === Vista previa ===
        preview_frame = QFrame()
        preview_layout = QHBoxLayout()
        preview_frame.setLayout(preview_layout)
        self.preview_label = QLabel("No preview")
        self.preview_label.setFixedSize(250, 180)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background:#fff; border:1px solid #dfeaf6;")
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_frame)

        # === Temporizador principal ===
        self.timer = QTimer()
        self.timer.timeout.connect(self.media_P_state)
        self.timer.start(1000)

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
                if hasattr(self, "output_path"):
                    ok = temp_file_manager.delete_with_retries(self.output_path)
                    if not ok:
                        print("⚠️ No se pudo borrar temporal:", self.output_path)
                self.cont_vid = 0
                self.play_video_prev()
        except Exception as e:
            log_message("ERROR", f"media_P_state: {e}")

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

        except Exception as e:
            QMessageBox.critical(self, "Error al abrir DB", str(e))
            self.update_status("❌ Error al inicializar la base de datos.")
            log_message("ERROR", f"select_db: {e}")

        finally:
            if hasattr(self, "timer") and not self.timer.isActive():
                self.timer.start(1000)
            log_message("INFO", "⏱️ Temporizador reactivado correctamente tras select_db().")

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
            event.accept()


# ======================================================================================
# FUNCIÓN PRINCIPAL
# ======================================================================================

def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(temp_file_manager.delete_all)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    main()
