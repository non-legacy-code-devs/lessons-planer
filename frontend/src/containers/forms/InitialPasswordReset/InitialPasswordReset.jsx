//react
import React, { useState } from 'react';
//redux
import { connect } from 'react-redux';
import {
  change_default_password,
  change_password_validation_error,
} from '../../../redux/actions/auth';
//router
import { Redirect } from 'react-router-dom';
//utils
import {
  BlueButton,
  Input,
  Wrapper,
} from '../../../components/styledComponents/index';
//font awesome:
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
//propTypes:
import PropTypes from 'prop-types';

const InitialPasswordReset = ({
  id,
  hasChangedPassword,
  change_default_password,
  change_password_validation_error,
}) => {
  InitialPasswordReset.propTypes = {
    id: PropTypes.number.isRequired,
    hasChangedPassword: PropTypes.bool,
    change_default_password: PropTypes.func.isRequired,
    change_password_validation_error: PropTypes.func.isRequired,
  };

  //FORM STATE:
  const [formData, setFormData] = useState({
    fb_name: '',
    old_password: '',
    new_password: '',
  });

  //STATES FOR VALIDATION:
  const [lowerCase, setLowerCase] = useState(false);
  const [upperCase, setUpperCase] = useState(false);
  const [numbers, setNumbers] = useState(false);
  const [specialCharacters, setSpecialCharacters] = useState(false);
  const [longEnough, setLongEnough] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  //STATES FOR EYEBALL:
  const [oldPasswordShown, setOldPasswordShown] = useState(false);
  const [newPasswordShown, setNewPasswordShown] = useState(false);

  //FORM:
  const { fb_name, old_password, new_password } = formData;

  const passwordValidation = (e) => {
    setChangingPassword(true);
    const lowerCase = /[a-z]/g;
    const upperCase = /[A-Z]/g;
    const numbers = /[0-9]/g;
    const specialCharacters = /[ `!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/g;

    lowerCase.test(e.target.value) ? setLowerCase(true) : setLowerCase(false);
    upperCase.test(e.target.value) ? setUpperCase(true) : setUpperCase(false);
    numbers.test(e.target.value) ? setNumbers(true) : setNumbers(false);
    specialCharacters.test(e.target.value)
      ? setSpecialCharacters(true)
      : setSpecialCharacters(false);
    e.target.value.length >= 8 ? setLongEnough(true) : setLongEnough(false);
  };
  const onChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  const onSubmit = (e) => {
    e.preventDefault();

    if (lowerCase && upperCase && numbers && specialCharacters && longEnough) {
      if (new_password !== old_password) {
        change_default_password(id, fb_name, old_password, new_password);
        setChangingPassword(false);
      } else {
        change_password_validation_error(
          'Stare i nowe has??o nie mog?? by?? identyczne!'
        );

        //TO DO: check similarity of passwords
      }
    } else {
      change_password_validation_error(
        'Nowe has??o nie spe??nia kryteri??w bezpiecze??stwa'
      );
    }
  };

  //TOGGLERS:
  const toggleOldPasswordShow = () => {
    setOldPasswordShown(oldPasswordShown ? false : true);
  };
  const toggleNewPasswordShow = () => {
    setNewPasswordShown(newPasswordShown ? false : true);
  };

  //REDIRECT:
  if (hasChangedPassword) {
    return <Redirect to="/" />;
  }
  return (
    <div className="min-h-100 py-5 py-lg-0 d-flex flex-column justify-content-center align-items-center">
      <Wrapper>
        <h1 className="title mb-4">Formularz resetowania has??a</h1>
        <form
          className="d-flex align-items-center flex-column"
          onSubmit={(e) => onSubmit(e)}
        >
          <p className="text">Wprowad?? nazw?? z facebook</p>
          <Input
            id="fb_name"
            type="text"
            className="mb-3 mb-md-4"
            placeholder="Adam Kowalski"
            name="fb_name"
            value={fb_name}
            onChange={(e) => onChange(e)}
            required
          />
          <p className="text">Podaj has??o tymczasowe</p>
          <div className="position-relative mb-3 mb-md-4">
            <Input
              id="password"
              type={oldPasswordShown ? 'text' : 'password'}
              placeholder="stare has??o"
              name="old_password"
              value={old_password}
              onChange={(e) => onChange(e)}
              required
            />
            <i
              className="position-absolute eye-icon"
              onClick={() => toggleOldPasswordShow()}
            >
              {<FontAwesomeIcon icon={oldPasswordShown ? faEyeSlash : faEye} />}
            </i>
          </div>
          <p className="text">Podaj nowe has??o</p>
          <div className="position-relative mb-3 mb-md-4">
            <Input
              id="new_password"
              type={newPasswordShown ? 'text' : 'password'}
              placeholder="nowe has??o"
              name="new_password"
              value={new_password}
              onChange={(e) => {
                onChange(e);
                passwordValidation(e);
              }}
              required
            />
            <i
              className="position-absolute eye-icon"
              onClick={() => toggleNewPasswordShow()}
            >
              {<FontAwesomeIcon icon={newPasswordShown ? faEyeSlash : faEye} />}
            </i>
          </div>
          <BlueButton className="mt-5" type="submit">
            wy??lij
          </BlueButton>
        </form>
      </Wrapper>

      {/* PASSWORD VALIDATION: */}
      {changingPassword ? (
        <Wrapper className="mt-5 mx-5">
          <div className="text-sm">
            <p className="m-0">
              Twoje nowe has??o powinno by?? nie kr??tsze ni??{' '}
              <span
                className={`fst-italic ${
                  longEnough ? 'text-green' : 'text-red'
                }`}
              >
                8 znak??w
              </span>{' '}
              i zawiera?? przynajmniej jeden/jedn??:{' '}
              <span
                className={`fst-italic ${
                  lowerCase ? 'text-green' : 'text-red'
                }`}
              >
                ma???? liter??
              </span>
              {', '}
              <span
                className={`fst-italic ${
                  upperCase ? 'text-green' : 'text-red'
                }`}
              >
                du???? liter??
              </span>
              {', '}
              <span
                className={`fst-italic ${numbers ? 'text-green' : 'text-red'}`}
              >
                cyfr??
              </span>
              {', '}
              <span
                className={`fst-italic ${
                  specialCharacters ? 'text-green' : 'text-red'
                }`}
              >
                znak specjalny
              </span>
              .
            </p>
          </div>
        </Wrapper>
      ) : null}
    </div>
  );
};

const mapStateToProps = (state) => ({
  id: state.auth.user?.id,
  hasChangedPassword: state.auth.user?.is_resetpwd,
});

export default connect(mapStateToProps, {
  change_default_password,
  change_password_validation_error,
})(InitialPasswordReset);
