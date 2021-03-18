import React, { useState } from 'react';
import axios from 'axios';

import InputButton from '../components/Buttons/InputButton';
import InputField from '../components/InputField/InputField';
import NavBar from '../components/NavBar/NavBar';
import { encryptStrings } from '../helpers';

import './Login.css';

function Login() {
  const [inputUsername, setUsername] = useState('');
  const [inputPassword, setPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!inputUsername || !inputPassword) {
      return;
    }
    const { encryptedUsername, encryptedPassword } = encryptStrings(
      { encryptedUsername: inputUsername },
      { encryptedPassword: inputPassword }
    );
    loginUser(encryptedUsername, encryptedPassword);
  };

  const loginUser = (username, password) => {
    axios
      .post('http://localhost:8008/api/auth/login', null, {
        params: { username, password },
      })
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <React.Fragment>
      <NavBar />
      <form onSubmit={handleSubmit} className='login'>
        <div className='login-container'>
          <h3>Login</h3>
          <div className='login-holder'>
            <InputField
              value='username'
              type='text'
              name='username'
              setProperty={setUsername}
            />
            <InputField
              value='password'
              type='password'
              name='password'
              setProperty={setPassword}
            />
            <InputButton name='Login'></InputButton>
          </div>
        </div>
      </form>
    </React.Fragment>
  );
}

export default Login;
