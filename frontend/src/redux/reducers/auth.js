import Cookies from 'js-cookie';
import {
  LOGIN_SUCCESS,
  LOGIN_FAIL,
  REGISTER_SUCCESS,
  REGISTER_FAIL,
  RESET_STATE,
  ACTIVATION_SUCCESS,
  ACTIVATION_FAIL,
  USER_LOADED_SUCCESS,
  USER_LOADED_FAIL,
  AUTHENTICATED_SUCCESS,
  AUTHENTICATED_FAIL,
  TOKEN_REFRESH_SUCCESS,
  TOKEN_REFRESH_FAIL,
  PASSWORD_RESET_SUCCESS,
  PASSWORD_RESET_FAIL,
  PASSWORD_RESET_CONFIRM_SUCCESS,
  PASSWORD_RESET_CONFIRM_FAIL,
  CHANGE_DEFAULT_PASSWORD_SUCCESS,
  CHANGE_DEFAULT_PASSWORD_FAIL,
  LOGOUT,
} from '../actions/types';

const initialState = {
  access: Cookies.get('access'),
  refresh: Cookies.get('refresh'),
  isAuthenticated: null,
  isSuperuser: null,
  loginSuccess: null,
  accountCreated: null,
  accountActivated: false,
  user: null,
  isLoading: false,
  defaultPasswordChanged: false,
};

export default function (state = initialState, action) {
  const { type, payload } = action;
  switch (type) {
    case RESET_STATE:
      return {
        ...state,
        accountCreated: null,
        accountActivated: false,
      };
    case AUTHENTICATED_SUCCESS:
      return {
        ...state,
        isAuthenticated: true,
      };
    case TOKEN_REFRESH_SUCCESS:
      Cookies.remove('access'); //redundant
      Cookies.remove('refresh'); //redundant code
      Cookies.set('access', payload.access);
      Cookies.set('refresh', payload.refresh);
      return {
        ...state,
        access: payload.access,
        refresh: payload.refresh,
      };
    case LOGIN_SUCCESS:
      Cookies.set('access', payload.access);
      Cookies.set('refresh', payload.refresh);
      return {
        ...state,
        access: payload.access,
        refresh: payload.refresh,
        loginSuccess: true,
      };
    case REGISTER_SUCCESS:
      return {
        ...state,
        accountCreated: true,
      };
    case REGISTER_FAIL:
      return {
        ...state,
        accountCreated: false,
      };
    case USER_LOADED_SUCCESS:
      return {
        ...state,
        user: payload,
        isSuperuser: payload.is_superuser,
        isAuthenticated: true,
      };
    case AUTHENTICATED_FAIL:
      return {
        ...state,
        isAuthenticated: false,
      };
    case TOKEN_REFRESH_FAIL:
      Cookies.remove('access');
      Cookies.remove('refresh');
      return {
        ...state,
        access: null,
        refresh: null,
        isAuthenticated: false,
      };
    case USER_LOADED_FAIL:
      return {
        ...state,
        user: null,
      };
    case LOGIN_FAIL:
      return {
        ...state,
        access: null,
        refresh: null,
        isAuthenticated: false,
        isSuperuser: null,
        loginSuccess: false,
        accountCreated: false,
        user: null,
      };
    case LOGOUT:
      Cookies.remove('access');
      Cookies.remove('refresh');
      return {
        ...state,
        access: null,
        refresh: null,
        isAuthenticated: false,
        isSuperuser: null,
        loginSuccess: null,
        accountCreated: false,
        user: null,
      };
    case CHANGE_DEFAULT_PASSWORD_SUCCESS:
      return {
        ...state,
        defaultPasswordChanged: true,
      };
    case CHANGE_DEFAULT_PASSWORD_FAIL:
      return {
        ...state,
        defaultPasswordChanged: false,
      };
    case ACTIVATION_SUCCESS:
      return {
        ...state,
        accountActivated: true,
      };
    case ACTIVATION_FAIL:
      return {
        ...state,
        accountActivated: false,
      };
    case PASSWORD_RESET_SUCCESS:
    case PASSWORD_RESET_FAIL:
    case PASSWORD_RESET_CONFIRM_SUCCESS:
    case PASSWORD_RESET_CONFIRM_FAIL:
      return {
        ...state,
      };
    default:
      return state;
  }
}
