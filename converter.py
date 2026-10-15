
# -*- coding: utf-8 -*-
#!/usr/bin/env python

from moviepy.editor import *
import os, sys

##=========================================================================================================
##=========================================================================================================

class Path():
    def resource_path(relative_path):
        """Get absolute path to resource, works for dev and for pyinstaller"""
        try:
            #PyInstaller Create a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

##=========================================================================================================
##=========================================================================================================

def convert(mp4_name, output_name):

    try:

        path_1 = Path.resource_path(mp4_name)
        path_2 = Path.resource_path(output_name)

        videoclip = VideoFileClip(path_1)
        audioclip = videoclip.audio
        audioclip.write_audiofile(path_2)
        audioclip.close()
        videoclip.close()

        return 'He Finalizado Exitosamente'

    except Exception as e:
        print(e)