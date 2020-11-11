import inspect
import logging

import cv2
import numpy as np

from consts import *


def get_median_height(input_dir):
    height = []
    total_images = 0
    folders_names = []
    try:
        # Folders name from input folder (e.g. "AshkenaziCursive", "BizantyCursive"...)
        folders_names.insert(0, os.path.join(input_dir, CURSIVE))
        folders_names.insert(1, os.path.join(input_dir, SEMI_SQUARE))
        folders_names.insert(2, os.path.join(input_dir, SQUARE))
    except FileNotFoundError:
        logging.error("[{}] - Input file '{}' not found.".format(inspect.stack()[0][3], INPUT_PATH))
        return  # The script can't run without input
    for input_path in folders_names:
        for subdir, dirs, _ in os.walk(input_path):
            for cur_dir in dirs:
                path = os.path.join(input_path, cur_dir)
                for image in os.listdir(path):
                    img_path = os.path.join(path, image)
                    i = cv2.imread(img_path)
                    if i is None:
                        new_img_path = os.path.join(path, str(total_images) + ".jpg")
                        os.rename(img_path, new_img_path)
                        print(f"Error in image: {img_path}, renaming to: {new_img_path}")
                        i = cv2.imread(new_img_path)
                    height.append(i.shape[0])
                    total_images += 1
                    print(f"image num: {total_images}, height: {i.shape[0]}")

    h = np.median(height)
    print(h)
    crop_images(input_dir, int(h))


def crop_images(input_dir, avg_height):
    folders_names = []
    total_images = 0
    try:
        # Folders name from input folder (e.g. "AshkenaziCursive", "BizantyCursive"...)
        folders_names.insert(0, os.path.join(input_dir, CURSIVE))
        folders_names.insert(1, os.path.join(input_dir, SEMI_SQUARE))
        folders_names.insert(2, os.path.join(input_dir, SQUARE))
    except FileNotFoundError:
        logging.error(f"[{inspect.stack()[0][3]}] - Input file '{INPUT_PATH}' not found.")
        return  # The script can't run without input
    for input_path in folders_names:
        for subdir, dirs, _ in os.walk(input_path):
            for cur_dir in dirs:
                path = os.path.join(input_path, cur_dir)
                for image in os.listdir(path):
                    img_path = os.path.join(path, image)
                    i = cv2.imread(img_path)
                    if i is None:
                        new_img_path = os.path.join(path, str(total_images) + ".jpg")
                        print(f"Error in image: {img_path}, renaming to: {new_img_path}")
                        os.rename(img_path, new_img_path)
                        img_path = new_img_path
                        i = cv2.imread(img_path)
                    print(f"\nimage: {img_path}")
                    h, w, _ = i.shape
                    ratio = h / w
                    print(f"old height: {h}, old width: {w}, ratio: {ratio}")

                    w = avg_height // ratio
                    ratio = avg_height / w
                    print(f"new hight: {avg_height}, new width: {int(w)}, ratio: {ratio}")

                    i = cv2.resize(i, (int(w), avg_height))

                    os.remove(img_path)

                    cv2.imwrite(img_path, i)
                    total_images += 1


crop_images("input_test", 4727)
