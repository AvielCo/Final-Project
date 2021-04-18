import { NavBar, ResultTextView } from '../../components';
import React, { useState, useEffect } from 'react';
import pic from '../../assets/landing-bg.jpg';
import { ToastContainer, toast } from 'react-toastify';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { getAccessToken } from '../../helpers';
import { Button, Upload } from 'antd';

import cursive from '../../assets/cursive_trans.png';

import 'react-toastify/dist/ReactToastify.css';
import './Home.css';

function LandingSection() {
  return (
    <section className="landing">
      <div></div>
      <p>
        Elit eiusmod elit ut id esse velit veniam ut consectetur esse occaecat quis sunt. Duis cupidatat qui sint ipsum amet exercitation enim et ipsum proident nostrud proident dolor. Incididunt
        officia voluptate aute commodo sit anim non et cupidatat cillum elit veniam. Irure anim aliquip enim officia anim voluptate minim mollit Lorem cillum. Consectetur est in magna labore nulla
        adipisicing ex aute Lorem. Cupidatat ipsum sit ut consequat minim aliquip consequat.
      </p>
    </section>
  );
}

function ScanSection({ isLoggedIn }) {
  const [imageUri, setImageUri] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState({
    success: false,
    origin: '',
    shape: '',
    probability: '',
  });

  const handleImageChange = async (info) => {
    switch (info.file.status) {
      case 'uploading':
        setIsLoading(true);
        break;
      case 'done':
        setIsLoading(false);
        setImageUri(URL.createObjectURL(info.file.originFileObj));
        break;
      case 'error':
        setIsLoading(false);
        break;
      default:
        break;
    }
  };

  const handlePredict = () => {
    if (!imageUri) {
      toast.error('Upload an image before predict.');
      return;
    }
    if (isLoading) {
      toast.info('Please wait, another predict process is running.');
      return;
    }
    toast.info('Predicting image, please wait.');
    setIsLoading(true);

    let accessToken = getAccessToken();

    const cfg = {
      headers: {
        Authorization: 'Bearer ' + accessToken,
      },
    };

    axios
      .post(`http://${process.env.REACT_APP_API_ADDRESS}:8008/api/images/scan`, null, cfg)
      .then((res) => {
        if (res.status === 200) {
          setResult(res.data);
          setIsLoading(false);
          toast.success('Predicting image done, see the result in your profile page.');
        }
      })
      .catch((err) => {
        if (err) {
          toast.error('An error has been encountered while trying to predict.');
          setIsLoading(false);
        }
      });
  };

  return (
    <section className="scan">
      <div className="scan-container">
        {isLoggedIn ? (
          <form className="scan-btn-holder" onSubmit={handleImageChange}>
            <h3>Scan Image</h3>
            <Upload
              action={`http://${process.env.REACT_APP_API_ADDRESS}:8008/api/images/upload`}
              headers={{ Authorization: 'Bearer ' + getAccessToken() }}
              onChange={handleImageChange}
              accept="image/*"
              maxCount={1}
              showUploadList={false}>
              <Button className="scan-btn" component="span" type="submit" loading={isLoading}>
                Upload an image
              </Button>
            </Upload>
            <Button className="scan-btn" onClick={handlePredict} loading={isLoading}>
              Predict selected image
            </Button>
            <ResultTextView result={result} />
          </form>
        ) : (
          <div>Login so you can scan</div>
        )}
        {imageUri && (
          <div className="scan-img-holder">
            <img alt={pic} src={imageUri}></img>
          </div>
        )}
      </div>
    </section>
  );
}

function AboutSection() {
  return (
    <section className="about">
      <div className="about-text-holder">
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
          nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
          proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        </p>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
          nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
          proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        </p>
      </div>
      <div className="image-rotate-holder">
        <img className="rotating-image" alt="something" src={cursive}></img>
      </div>
    </section>
  );
}

function WWASection() {
  return <section className="wwa"></section>;
}

function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const history = useHistory();

  useEffect(() => {
    if (isLoggedIn) return;
    const cfg = {
      headers: {
        Authorization: 'Bearer ' + getAccessToken(),
      },
    };
    axios
      .get(`http://${process.env.REACT_APP_API_ADDRESS}:8008/api/auth/user`, cfg)
      .then((res) => {
        if (res.status === 200) {
          setIsLoggedIn(true);
        }
      })
      .catch((err) => {
        if (err.response) {
          const { status, message } = err.response.data.error;
          if (status === 404) {
            history.replace('/404');
            return;
          }
          toast.info('Please log in to upload and predict an image.');
        }
      });
  }, [isLoggedIn]);

  return (
    <>
      <ToastContainer position="top-left" autoClose={5000} hideProgressBar={false} newestOnTop closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover />
      <div className="home">
        <NavBar isLoggedIn={isLoggedIn} />
        <LandingSection />
        <ScanSection isLoggedIn={isLoggedIn} />
        <AboutSection />
        <WWASection />
      </div>
    </>
  );
}
export default Home;
