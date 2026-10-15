
# stability_patch_v1.py
# --------------------------------------------------------------------
# Módulo de estabilidad para proyectos PyQt5
# Autor: ✦ Cristian M. Veliz Cano
# Descripción:
#   Ofrece cierre seguro, monitoreo de hilos y control de temporizadores
#   sin alterar la estructura del proyecto base.
# --------------------------------------------------------------------

import os, sys, time, traceback
from datetime import datetime

LOG_FILE = "stable_log.txt"

def log_message(level, message):
    """Registra mensaje en consola y archivo."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{stamp}] [{level}] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass


def protect_window(cls):
    """
    Decorador que refuerza clases QMainWindow (u otras)
    agregando un cierre seguro, protección de hilos y temporizadores.
    """
    orig_close = getattr(cls, "closeEvent", None)

    def safe_close(self, event):
        try:
            log_message("INFO", "Ejecutando cierre seguro del sistema...")

            # 1. Detener temporizadores
            if hasattr(self, "timer") and self.timer.isActive():
                self.timer.stop()
                log_message("INFO", "Temporizador detenido correctamente.")

            # 2. Detener reproducción multimedia
            if hasattr(self, "mediaPlayer"):
                try:
                    self.mediaPlayer.stop()
                    if hasattr(self, "playlist"):
                        self.playlist.clear()
                    log_message("INFO", "MediaPlayer detenido.")
                except Exception as e:
                    log_message("WARN", f"No se pudo detener mediaPlayer: {e}")

            # 3. Terminar hilos activos
            for worker_name in ("_insert_worker", "_extract_worker"):
                worker = getattr(self, worker_name, None)
                if worker and worker.isRunning():
                    try:
                        worker.terminate()
                        worker.wait()
                        log_message("INFO", f"Hilo {worker_name} terminado.")
                    except Exception as e:
                        log_message("WARN", f"Error deteniendo hilo {worker_name}: {e}")

            # 4. Limpieza de archivos temporales
            try:
                if "temp_file_manager" in globals():
                    globals()["temp_file_manager"].delete_all()
                    log_message("INFO", "Archivos temporales limpiados.")
            except Exception as e:
                log_message("WARN", f"No se pudo limpiar archivos temporales: {e}")

            log_message("INFO", "Cierre completo sin errores.")

        except Exception as e:
            traceback.print_exc()
            log_message("ERROR", f"Excepción durante cierre: {e}")

        finally:
            if orig_close:
                orig_close(self, event)
            else:
                event.accept()

    cls.closeEvent = safe_close
    return cls


def monitor_timer(timer, interval=1000):
    """Asegura que el temporizador se mantenga activo y reiniciable."""
    try:
        if not timer.isActive():
            timer.start(interval)
            log_message("INFO", "⏱️ Temporizador reactivado automáticamente.")
    except Exception as e:
        log_message("ERROR", f"No se pudo reiniciar temporizador: {e}")


def guard_thread(worker):
    """Envuelve un QThread con manejo de error controlado."""
    if not worker:
        return None

    try:
        if worker.isRunning():
            log_message("INFO", f"Hilo {worker.objectName()} ya en ejecución.")
        else:
            worker.start()
            log_message("INFO", f"Hilo {worker.objectName()} iniciado correctamente.")
    except Exception as e:
        log_message("ERROR", f"No se pudo iniciar hilo: {e}")
    return worker


# --------------------------------------------------------------------
# Uso:
# --------------------------------------------------------------------
# from stability_patch_v1 import protect_window, log_message, monitor_timer
#
# @protect_window
# class MainWindow(QMainWindow):
#     ...
#
# Y en cualquier parte del código:
#     monitor_timer(self.timer)
#     log_message("INFO", "Mensaje de estado")
#
# --------------------------------------------------------------------
