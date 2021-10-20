import React, { useState } from 'react';
import {
	StyledLoginBox,
	StyledInput,
	StyledBlueButton,
} from '../../components/styledComponents/index';
import { Link, Redirect } from 'react-router-dom';
import { connect } from 'react-redux';
import { login } from '../../redux/actions/auth';

import PropTypes from 'prop-types';

const LoginForm = ({ login, isAuthenticated, errorMsg }) => {
	LoginForm.propTypes = {
		login: PropTypes.func,
		isAuthenticated: PropTypes.bool,
		errorMsg: PropTypes.string || PropTypes.object,
	};

	const [formData, setFormData] = useState({
		username: '',
		password: '',
	});

	const { username, password } = formData;

	const onChange = (e) =>
		setFormData({ ...formData, [e.target.name]: e.target.value });

  return (
    <div className="d-flex justify-content-center align-items-center loginForm">
      <StyledLoginBox className="d-flex justify-content-center">
        <form
          className="d-flex justify-content-center align-items-center flex-column"
          onSubmit={(e) => onSubmit(e)}
        >
          <h1 className="title mb-4">Logowanie do platformy</h1>
          <StyledInput
            id="name"
            type="text"
            placeholder="login"
            className="mb-4"
            name="username"
            value={username}
            onChange={(e) => onChange(e)}
            required
          />
          <StyledInput
            id="password"
            type="password"
            placeholder="hasło"
            name="password"
            value={password}
            onChange={(e) => onChange(e)}
            required
          />
          <StyledBlueButton type="submit" className="mt-4 px-5 py-2">
            zaloguj się
          </StyledBlueButton>
          <Link className="mt-3 link" to="/reset_password">
            zapomniałem hasła
          </Link>
        </form>
      </StyledLoginBox>
    </div>
  );
};

const mapStateToProps = (state) => ({
	isAuthenticated: state.auth.isAuthenticated,
	errorMsg: state.errors.msg,
	errorStatus: state.errors.status,
});

export default connect(mapStateToProps, { login })(LoginForm);
