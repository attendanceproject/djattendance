import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { applyMiddleware, combineReducers, compose, createStore } from 'redux'
import {reducer as formReducer} from 'redux-form'
import thunkMiddleware from 'redux-thunk'
import { AppContainer } from 'react-hot-loader'

import Attendance from './containers/Attendance'
import Calendar from './components/Calendar'
import combined from './reducers/reducer'
import initialState from './initialstate'

// scss imports
import '../scss/index.css'
import 'font-awesome/scss/font-awesome.scss'
import 'react-select/scss/default.scss'
import 'react-widgets/dist/css/react-widgets.css'
import '../scss/ap_react.scss'

const store = createStore(combined, initialState, compose(
  applyMiddleware(thunkMiddleware),
  window.devToolsExtension ? window.devToolsExtension() : f => f //redux chrome dev tools
));
window.store = store;

const render = (Component, root) => {
  if (!root) {
    return;
  }
  ReactDOM.render(
    <AppContainer>
      <Provider store={store}>
        <Component />
      </Provider>
    </AppContainer>,
    root
  )
}

let attendanceRoot = document.getElementById('react-attendance-root');
let calendarRoot = document.getElementById('react-calendar-root');

render(
  Attendance, attendanceRoot
);
render(
  Calendar, calendarRoot
);

if (module.hot) {
  module.hot.accept('./containers/Attendance', () => {
    render(Attendance, attendanceRoot);
  });
  module.hot.accept('./components/Calendar', () => {
    render(Calendar, calendarRoot);
  });
}
