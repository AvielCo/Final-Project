import React, { useState, useEffect } from "react";
import { useHistory } from "react-router-dom";
import axios from "axios";
import "./Login.css";
import { Checkbox, Form } from "antd";
import { InputButton, InputField } from "../../components";
import { encryptStrings, getAccessToken } from "../../helpers";
import { UserOutlined, LockOutlined } from "@ant-design/icons";

import "./Login.css";

function Login() {
  const [form] = Form.useForm();

  const [inputUsername, setUsername] = useState("");
  const [inputPassword, setPassword] = useState("");
  const history = useHistory();
  const [checked, setChecked] = useState(false);

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
      .post("http://localhost:8008/api/auth/login", { username, password })
      .then((response) => {
        if (response.status === 200) {
          window.sessionStorage.setItem(
            "accessToken",
            response.data.accessToken
          );
          if (checked) {
            window.localStorage.setItem(
              "accessToken",
              response.data.accessToken
            );
          }
          history.replace("/");
          return;
        }
        //TODO: show error
        //!garachia kartoshta

        return;
      })
      .catch((error) => {
        console.log(error);
      });
  };

  useEffect(() => {
    const accessToken = getAccessToken();
    if (accessToken) {
      history.replace("/");
    }
  });
  //garachia kartoshta
  return (
    <React.Fragment>
      <form onSubmit={handleSubmit} className="login">
        <div className="login-container">
          <h3>Login</h3>
          <div className="login-holder">
            <Form.Item
              name="username"
              label="Username"
              rules={[
                { required: true, message: "Please enter your username." },
                { type: "text", message: "Please enter a valid username." },
              ]}
            >
              <Form.Item
                name="password"
                label="Password"
                rules={[
                  { required: true, message: "Please input your Password!" },
                ]}
              >
                <InputField
                  value="password"
                  type="password"
                  name="password"
                  setProperty={setPassword}
                  prefix={<LockOutlined />}
                />
              </Form.Item>
            </Form.Item>
            <InputField
              value="password"
              type="password"
              name="password"
              setProperty={setPassword}
            />
            <Checkbox
              checked={checked}
              onChange={(e) => setChecked(e.target.checked)}
            >
              Remember me
            </Checkbox>
            <InputButton name="Login" type="submit"></InputButton>
          </div>
        </div>
      </form>
    </React.Fragment>
  );
}

export default Login;
