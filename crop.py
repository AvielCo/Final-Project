import os
import logging
import inspect
from pytz import timezone
import concurrent.futures
from datetime import datetime, timedelta
import cv2
import subprocess
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image

# Global variables
NUM_OF_CROPPED_IMAGES = 0
NUM_OF_PATCHES = 0
# Threads
NUM_OF_THREADS = 2

# Logger
tz = timezone('Asia/Jerusalem')


def timetz(*args):
    return datetime.now(tz).timetuple()


logging.Formatter.converter = timetz

# Dirs
PROJECT_DIR = os.getcwd()
INPUT_PATH = os.path.join(PROJECT_DIR, "input")
OUTPUT_PATH = os.path.join(PROJECT_DIR, "output")
UNFILTERED_PATCHES_PATH = os.path.join(PROJECT_DIR, "unfiltered_patches")
CURSIVE = "cursive"
SEMI_SQUARE = "semi_square"
SQUARE = "square"
CURSIVE_INPUT_PATH = os.path.join(INPUT_PATH, CURSIVE)
SEMI_SQUARE_INPUT_PATH = os.path.join(INPUT_PATH, SEMI_SQUARE)
SQUARE_INPUT_PATH = os.path.join(INPUT_PATH, SQUARE)
CURSIVE_UNFILTERED_PATH = os.path.join(UNFILTERED_PATCHES_PATH, CURSIVE)
SEMI_SQUARE_UNFILTERED_PATH = os.path.join(UNFILTERED_PATCHES_PATH, SEMI_SQUARE)
SQUARE_UNFILTERED_PATH = os.path.join(UNFILTERED_PATCHES_PATH, SQUARE)
CURSIVE_OUTPUT_PATH = os.path.join(OUTPUT_PATH, CURSIVE)
SEMI_SQUARE_OUTPUT_PATH = os.path.join(OUTPUT_PATH, SEMI_SQUARE)
SQUARE_OUTPUT_PATH = os.path.join(OUTPUT_PATH, SQUARE)

# Page details
# Single page dimensions

PATCH_DIMENSIONS = {"x": 500, "y": 500, "xOffset": 500 // 2, "yOffset": 500 // 2}


def cropSinglePage(imageName: str, folderName: str):
    """
    This function crops a single page from the scan (by its dimensions).

    Parameters:
    imageName (str): The name of the scanned image.
    dimensionsDict (dict): The dimensions of the scanned image.
    folderName (str): The name of the folder that the scan is saved in.
    """
    print(os.path.join(INPUT_PATH, folderName, imageName))
    img = cv2.imread(os.path.join(INPUT_PATH, folderName, imageName),
                     0)  # Read the image from the folder with grayscale mode
    originalName = imageName  # For the log
    dims = img.shape
    h, w = dims[0], dims[1]
    saveName = os.path.splitext(imageName)[0]
    newImg = RGBtoBW(img)
    cropToPatches(newImg, saveName, w, h, folderName)
    logging.info("[" + inspect.stack()[0][3] + "] - " + "Image " + originalName + " Cropped successfully.")


def RGBtoBW(img):
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite("test.jpg", thresh)
    return thresh


def cropFiles(imagesInput, folderName: str):
    """
    This function calls cropSinglePage for each image in the imagesInput list, with its dimensions and input folder name.

    Parameters:
    imagesInput (list): List of images from the same input folder.
    dimensionsDict (dict): The dimensions of the images.
    folderName (str): Input folder of the images.
    """
    for imageName in imagesInput:
        cropSinglePage(imageName, folderName)


def listToChunks(l, n):
    """fu ck u em ilia
    This function divides the images into chunks so that the threads could work on each chunk.

    Prameters:
    l(list): List of images.
    n(int): Number of chunks.

    Returns:
    list: each chunk as a list of images.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def runThreads(folderName: str):
    """
    This function creates output folders and runs threads on each chunk of images.

    Parameters:
    folderName(str): The name of the images folder inside output folder.
    dimensionsDict(dict): The dimension of the scanned images.
    """
    path = os.path.join(INPUT_PATH, folderName)
    try:
        imagesInput = os.listdir(path)  # Get all of the images from the current folder
    except FileNotFoundError:
        logging.error("[" + inspect.stack()[0][3] + "] - Input file '" + path + "' not found.")
        return
    if not os.path.exists(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)  # Create output folder
    if not os.path.exists(os.path.join(OUTPUT_PATH, folderName)):
        os.mkdir(os.path.join(OUTPUT_PATH, folderName))  # Create a folder inside output folder
    global NUM_OF_THREADS
    if NUM_OF_THREADS == 1:  # Prevent division by zero
        NUM_OF_THREADS += 1
    i = round(len(imagesInput) // (NUM_OF_THREADS - 1))
    chunks = list(listToChunks(imagesInput, i))  # Divide the images into chunks for the threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_OF_THREADS) as executor:  # A thread pool for the threads
        for i in range(NUM_OF_THREADS):
            try:
                executor.submit(cropFiles, chunks[i], folderName)  # Add thread to the pool with its chunk
            except IndexError:
                continue


def cropToPatches(image, imageName: str, imageWidth: int, imageHeight: int, folderName: str):
    """
    This function takes a page, crops it into patches of 300X200 pixels and saves them in output folder.

    Parameters:
    image (list): List of pixels represented the RBG of the image.
    imageName (str): The name of the image.
    imageWidth (int): The width (X axis) of the image.
    imageHeight (int): The height (Y axis) of the image.
    folderName (str): The name of the output folder.
    """
    x1 = y1 = 0
    x2, y2 = PATCH_DIMENSIONS["x"], PATCH_DIMENSIONS["y"]  # The dimension of the patch (current: 300X200)
    xOffset, yOffset = PATCH_DIMENSIONS["xOffset"], PATCH_DIMENSIONS[
        "yOffset"]  # The offset of the patch (defined as 1/3 the size of the patch)
    i = 1  # Index for naming each patch
    while x2 < imageWidth:  # End of pixels row
        j = 0  # Index for Y axis offset
        while y2 + yOffset * j < imageHeight:  # End of pixels col
            croppedPatch = image[y1 + yOffset * j: y2 + yOffset * j, x1: x2]  # Extract the pixels of the selected patch
            saveLocation = os.path.join(UNFILTERED_PATCHES_PATH, folderName, imageName + str(i) + ".jpg")
            global NUM_OF_PATCHES
            NUM_OF_PATCHES += 1  # Patches counter
            if countPixels(croppedPatch):
                plt.imsave(saveLocation, croppedPatch)  # Save the patch to the output folder
            i += 1
            j += 1
        x1 += xOffset
        x2 += xOffset


def countPixels(img):
    n = PATCH_DIMENSIONS['x'] // 2
    h, w = img.shape
    splitted_img = []
    k = 0
    cv2.imshow("aa", img)
    cv2.waitKey(0)
    for y in range(0, h, n):
        for x in range(0, w, n):
            y1 = y + n
            x1 = x + n
            splitted_img.insert(k, img[y: y1, x:x1])
            cv2.imshow("aa", splitted_img[k])
            cv2.waitKey(0)
            k += 1

    summ = []
    for i in range(4):
        darkPixels = n * n - cv2.countNonZero(splitted_img[i])
        summ.insert(i, darkPixels / (n ** 2))

    return True


def preProcessingMain():
    """
    This function loads the folder names from the input folder and executes the crop algorithm on each name, with its crop dimestions.
    """
    folders_names = []
    try:
        # Folders name from input folder (e.g. "AshkenaziCursive", "BizantyCursive"...)
        folders_names.insert(0, CURSIVE_INPUT_PATH)
        folders_names.insert(1, SQUARE_INPUT_PATH)
        folders_names.insert(2, SEMI_SQUARE_INPUT_PATH)
    except FileNotFoundError:
        logging.error("[" + inspect.stack()[0][3] + "] - Input file '" + INPUT_PATH + "' not found.")
        return  # The script can't run without input
    logging.info("[" + inspect.stack()[0][3] + "] - " + "Deleting output folder")
    # subprocess.call("rm -rf " + OUTPUT_PATH + os.sep + "*", shell=True) # Delete output folder
    logging.info("[" + inspect.stack()[0][3] + "] - " + "Done")
    for name in foldersName:
        logging.info("[" + inspect.stack()[0][3] + "] - " + "Start cropping the folder " + name + ".")
        try:
            runThreads(name)  # Pass the folder name and its dimensions
            logging.info("[" + inspect.stack()[0][3] + "] - " + "Cropping of " + name + " succeeded.")
        except KeyError:
            logging.error("[" + inspect.stack()[0][
                3] + "] - File name doesn't match to the dimensions dictionary's key.")  # In case the folder name is incorrect,
            # or the dimensions dict doesn't contain the folder dimensions
            logging.error("[" + inspect.stack()[0][3] + "] - Cropping of " + name + " Failed.")


def checkIfFolderExists(input_path):
    if os.path.exists(input_path):
        return True
    return False


def createFolders():
    # CREATE INPUT PATHS
    if not checkIfFolderExists(CURSIVE_INPUT_PATH):
        os.makedirs(CURSIVE_INPUT_PATH)
    if not checkIfFolderExists(SQUARE_INPUT_PATH):
        os.makedirs(SQUARE_INPUT_PATH)
    if not checkIfFolderExists(SEMI_SQUARE_INPUT_PATH):
        os.makedirs(SEMI_SQUARE_INPUT_PATH)

    # CREATE UNFILTERED PATCHES PATHS
    if not checkIfFolderExists(CURSIVE_UNFILTERED_PATH):
        os.makedirs(CURSIVE_UNFILTERED_PATH)
    if not checkIfFolderExists(SQUARE_UNFILTERED_PATH):
        os.makedirs(SQUARE_UNFILTERED_PATH)
    if not checkIfFolderExists(SEMI_SQUARE_UNFILTERED_PATH):
        os.makedirs(SEMI_SQUARE_UNFILTERED_PATH)

    # CREATE OUTPUT PATHS
    if not checkIfFolderExists(CURSIVE_OUTPUT_PATH):
        os.makedirs(CURSIVE_OUTPUT_PATH)
    if not checkIfFolderExists(SQUARE_OUTPUT_PATH):
        os.makedirs(SQUARE_OUTPUT_PATH)
    if not checkIfFolderExists(SEMI_SQUARE_OUTPUT_PATH):
        os.makedirs(SEMI_SQUARE_OUTPUT_PATH)




def main():
    """
    Main function with execution time logging.
    """
    startTime = datetime.now()
    logging.info("[" + inspect.stack()[0][3] + "] - " + "Crop Script started")
    createFolders()
    # preProcessingMain()
    logging.info(
        "[" + inspect.stack()[0][3] + "] - " + "Crop Script ended, execution time: " + str(datetime.now() - startTime))
    logging.info(
        "[" + inspect.stack()[0][3] + "] - " + str(NUM_OF_CROPPED_IMAGES) + " Images have been cropped into " + str(
            NUM_OF_PATCHES) + " Patches.")


if __name__ == "__main__":
    main()
