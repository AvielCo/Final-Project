const express = require('express');
const createError = require('http-errors');
const { verifyAccessToken } = require('../../../helpers/jwt');
const User = require('../../../models/User');
const History = require('../../../models/History');
const router = express.Router();
const exec = require('child_process').exec;
const path = require('path');
const uploadFile = require('../../../helpers/upload');
const fs = require('fs');
const sharp = require('sharp');

const insertNewHistory = async (userHistory, newHistory, imageName) => {
  let { predictedResult } = userHistory;
  if (!predictedResult) {
    predictedResult = { classes: [], probabilities: [], dates: [] };
  }
  predictedResult.classes.push(`${newHistory.origin} ${newHistory.shape}`);
  predictedResult.probabilities.push(newHistory.probability);
  predictedResult.dates.push(new Date());
  predictedResult.images.push(imageName);
  await History.findByIdAndUpdate({ _id: userHistory._id }, { predictedResult });
};

const genRandomString = (length) => {
  let randomChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += randomChars.charAt(Math.floor(Math.random() * randomChars.length));
  }
  return result;
};

router.post('/upload', verifyAccessToken, async (req, res, next) => {
  try {
    await uploadFile(req, res)
      .then(() => res.status(200).send('Image uploaded successfully.'))
      .catch((err) => {
        throw createError.BadRequest('Not uploaded');
      });
  } catch (err) {
    next(err);
  }
});

router.post('/scan', verifyAccessToken, async (req, res, next) => {
  try {
    const user = await User.findOne({ _id: req.payload.aud });

    const pythonScript = 'predict.py';
    const pythonScriptPath = path.join(__dirname, '..', 'py-files', pythonScript);
    const pythonScriptCommand = `python ${pythonScriptPath}  ${user._id}`;
    const envName = 'py36';
    const condaCommand = `conda run -n ${envName}`;
    const child = exec(`${condaCommand} ${pythonScriptCommand}`);

    child.stdout.on('data', async (data) => {
      // message is the response from python script
      const message = JSON.parse(data);
      if (message.success) {
        /**
         * message: {
         *  success: True,
         *  origin: One of the following: "ashkenazi", "bizantine" .....
         *  shape: One of the following: "cursive", "square", "semi-square"
         *  probability: the probability of the prediction
         * }
         */
        try {
          let totalImages = 0; // total images that the user has seen predicted
          const imagePath = path.join(__dirname, '..', 'python-folders', 'predict-files', 'predict_images', `${user._id}`, 'imageToUpload.jpg');
          const userHistory = await History.findById({ _id: user.historyId });
          if (userHistory.predictedResult.classes.length > 0) {
            // get the amount of the images that the user has predicted so far.
            totalImages = userHistory.predictedResult.classes.length;
          }
          // path to save the resized image to view later in the user profile
          const savePath = path.join(__dirname, '..', 'users-histories', `${user._id}`);
          fs.mkdir(savePath, { recursive: true }, (err) => {
            if (err) throw createError.InternalServerError();
          });

          // generate unique hash for image name
          const imageName = genRandomString(40);

          sharp(imagePath) // resize the image to width: 250px (height is auto scale)
            .resize(250)
            .toFile(path.join(savePath, `${imageName}.jpg`))
            .catch((err) => {
              if (err) throw createError.InternalServerError();
            });

          await insertNewHistory(userHistory, message, imageName);

          return res.status(200).send(message);
        } catch (err) {
          console.log(err);
          return next(createError.InternalServerError());
        }
      }
      /**
       * message: {
       *  success: False,
       * `reason: Reason that the script failed
       * }
       */
      console.log(message.reason);
      return next(createError.BadRequest());
    });

    child.stderr.on('data', (data) => {
      console.log(data);
    });

    child.on('error', function (err) {
      throw next(createError.InternalServerError());
    });
  } catch (err) {
    console.log(err);
    next(err);
  }
});

module.exports = router;
