import cv2
import os
import subprocess

def write_first_frame(upload_dir: str, hash: str, ext: str):
    filepath = os.path.join(upload_dir, hash + ext)
    imgpath = os.path.join(upload_dir, hash + ".jpg")
    ffmpeg_command = [
        'ffmpeg', '-y', '-i', filepath, '-vf', 'select=eq(n\\,0)', '-frames:v', '1', imgpath
    ]

    subprocess.run(ffmpeg_command)
