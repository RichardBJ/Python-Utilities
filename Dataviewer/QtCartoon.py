import sys
import os
import glob
import re
import imageio.v2 as imageio
from skimage.transform import resize
from PyQt5.QtWidgets import QApplication, QFileDialog
from PIL import Image, ImageDraw, ImageFont

def select_files():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg *.bmp)")
    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        return selected_files
    return []

def resize_images(filenames, target_size):
    resized_images = []
    for filename in filenames:
        image = imageio.imread(filename)
        resized_image = resize(image, target_size, anti_aliasing=True)
        resized_image = (resized_image * 255).astype('uint8')  # Convert to uint8
        resized_images.append(resized_image)
    return resized_images

def create_mp4(filenames, output_dir, fps=5):
    anim_file = os.path.join(output_dir, 'movie.mp4')
    filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
    target_size = imageio.imread(filenames[0]).shape[:2]
    resized_images = resize_images(filenames, target_size)
    with imageio.get_writer(anim_file, fps=fps) as writer:
        for image in resized_images:
            writer.append_data(image)

def create_gif(filenames, output_dir, fps=1):
    anim_file = os.path.join(output_dir, 'movie.gif')
    filenames.sort(key=lambda f: int(re.sub('\D', '', f)))
    target_size = imageio.imread(filenames[0]).shape[:2]
    resized_images = resize_images(filenames, target_size)
    decimate = 2
    with imageio.get_writer(anim_file, fps=fps) as writer:
        for count, image in enumerate(resized_images):
            if count % decimate == 0:
                writer.append_data(image)

if __name__ == "__main__":
    selected_files = select_files()
    if selected_files:
        output_dir = os.path.dirname(selected_files[0])
        create_mp4(selected_files, output_dir)
        create_gif(selected_files, output_dir)
    else:
        print("No files selected.")