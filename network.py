import gc
import logging as log
from datetime import datetime

import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.compat.v1 import InteractiveSession, ConfigProto
from tensorflow.keras.utils import to_categorical
from tensorflow_core.python.keras.saving.save import load_model

from callbacks import *
from consts import *
from dual_print import dual_print
from general import buildData
from models import *


def main(input_folder, run_crop=True, times=1):
    # GPU configuration
    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)

    # Const variables

    # Batch size for fit function for each step in epoch
    BATCH_SIZE = 128

    prog_init_start_time = datetime.now()

    filename = f"{datetime.now().strftime('%d-%m-%y--%H-%M')}_train_on={input_folder}"
    log.basicConfig(format="%(asctime)s--%(levelname)s: %(message)s",
                    datefmt="%H:%M:%S",
                    filename=filename,
                    level=log.INFO)
    for j in range(times):
        start_time = datetime.now()
        # Cache flag from command line
        df1, y1 = buildData(input_folder, "output", run_crop)  # True = Starting crop process
        dual_print("Converting data to Numpy array")
        log.info("Converting data to Numpy array")
        saved_time = datetime.now()
        df = np.asarray(df1)
        dual_print(f"Done, took: {datetime.now() - saved_time}")
        dual_print("Calling Garbage Collector")
        del df1
        gc.collect()
        dual_print("Done")
        dual_print("Reshaping Grayscale data for Conv2D dimesions")
        df = df.reshape((df.shape[0], df.shape[1], df.shape[2], 1))
        dual_print("Done")
        dual_print("Converting Y to categorical matrix")
        saved_time = datetime.now()
        y = to_categorical(y1)
        dual_print(f"Done, took: {str(datetime.now() - saved_time)}")
        dual_print("Calling Garbage Collector")
        del y1
        gc.collect()
        dual_print("Done")
        dual_print("Splitting data into train and test")
        saved_time = datetime.now()
        X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=TEST_PERCENT, random_state=42)
        inputShape = (df.shape[1], df.shape[2], df.shape[3])
        dual_print(f"Done, took: {str(datetime.now() - saved_time)}")
        dual_print("Calling Garbage Collector")
        del y
        del df
        gc.collect()
        dual_print("Done")

        # Create model
        dual_print("Loading model...")
        if os.path.exists(os.path.join(os.getcwd(), "BestModel.h5")):
            model = load_model("BestModel.h5")
        else:
            dual_print("No model found, creating..")
            model = default_model_architecture(inputShape)

        dual_print("Done")
        # Save the best model
        dual_print("Creating callbacks")

        if not os.path.exists(os.path.join(PROJECT_DIR, "checkpoints", "val_loss")):
            os.makedirs(os.path.join(PROJECT_DIR, "checkpoints", "val_loss"))

        if not os.path.exists(os.path.join(PROJECT_DIR, "checkpoints", "val_categorical_accuracy")):
            os.makedirs(os.path.join(PROJECT_DIR, "checkpoints", "val_categorical_accuracy"))

        if not os.path.exists(os.path.join(PROJECT_DIR, "checkpoints", "val_accuracy")):
            os.makedirs(os.path.join(PROJECT_DIR, "checkpoints", "val_accuracy"))

        callbacks = [checkpoint_best, checkpoint_val_accuracy, tensorboard]

        model.summary(print_fn=print)
        dual_print("Running the model")

        # Train the model
        history = model.fit(X_train, y_train,
                            validation_data=(X_test, y_test),
                            epochs=50,
                            verbose=0,
                            batch_size=BATCH_SIZE,
                            callbacks=callbacks)

        dual_print(f"Done training.\nThe process took: {str(datetime.now() - start_time)}"
                   f"\n\n\n ------------------------------------------------------------")

        i = 0
        while True:
            output_path_new_name = f"{crop.OUTPUT_PATH}_{str(i)}"
            if not os.path.exists(output_path_new_name):
                os.rename(crop.OUTPUT_PATH, output_path_new_name)
                break
            i += 1

    dual_print(f"Done training in loop. Time took to train: {str(datetime.now() - prog_init_start_time)} ")
    log.shutdown()
    os.rename(filename, filename + "__DONE.txt")
