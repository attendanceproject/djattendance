//set manipulations used to do array computations easily from https://www.npmjs.com/package/set-manipulator
import { union, intersection, difference, complement, equals } from 'set-manipulator';

import { CHANGE_DATE, SUBMIT_ROLL, UPDATE_ATTENDANCE, UPDATE_EVENTS, UPDATE_TRAINEE_VIEW, TOGGLE_EVENT,
          DESELECT_EVENT, DESELECT_ALL_EVENTS, DESTROY_LEAVESLIP, SUBMIT_LEAVESLIP, SUBMIT_GROUPSLIP, DESTROY_GROUPSLIP,
          CHANGE_TRAINEE_VIEW, CHANGE_LEAVESLIP_FORM, CHANGE_GROUPSLIP_FORM, SHOW_CALENDAR, CHANGE_ROLL_FORM, RESET_ROLL_FORM,
          RESET_LEAVESLIP_FORM, RESET_GROUPSLIP_FORM, TOGGLE_LEGEND, EDIT_LEAVESLIP, EDIT_GROUP_LEAVESLIP
          } from '../actions';
import { SLIP_TYPE_LOOKUP, TA_IS_INFORMED, TA_EMPTY } from '../constants'
import initialState from '../initialstate'
import { combineReducers } from 'redux'
import { addDays } from 'date-fns'

function date(state = initialState.date, action) {
  switch (action.type) {
    case CHANGE_DATE:
      return addDays(state, action.days)
    default:
      return state;
  }
}

function rolls(state = initialState.rolls, action) {
  switch (action.type) {
    //Async related (action.roll is returned from ajax call)
    case UPDATE_ATTENDANCE:
      return action.attendance.rolls
    case SUBMIT_ROLL:
      //remove all old rolls with complement (arr1-arr2)
      //merge with new rolls
      //create a unique id combining events and dates (e<event_id>) asdfadsfd
      var rolls = [
        ...complement(state, action.rolls, (o) => 'e' + o.event.toString() +'-d' + o.date.toString()),
        ...action.rolls
      ]
      console.log('amirite', state, action.rolls, complement(state, action.rolls, (o) => 'e' + o.event.toString() +'-d' + o.date.toString()));
      return rolls;
    default:
      return state;
  }
}

function form(state=initialState.form, action) {
  if ([EDIT_LEAVESLIP, EDIT_GROUP_LEAVESLIP].includes(action.type)) {
    var slip = action.slip
    var informed = TA_IS_INFORMED.id
    if (!(slip.informed || slip.texted)) {
      informed = 'false'
    } else if (slip.texted) {
      informed = 'texted'
    }
  }

  switch(action.type) {
    case EDIT_LEAVESLIP:
      return Object.assign({}, state, { leaveSlip: {
          ...slip,
          hostPhone: slip.host_phone,
          hostName: slip.host_name,
          hcNotified: slip.hc_notified,
          description: slip.description,
          slipType: {
            id: slip.type,
            name: SLIP_TYPE_LOOKUP[slip.type]
          },
          ta: {
            id: slip.TA_informed
          },
          ta_informed: {
            id: informed
          },
        }
      })

    case EDIT_GROUP_LEAVESLIP:
      return Object.assign({}, state, {
        groupSlip: {
          ...slip,
          description: slip.description,
          slipType: {
            id: slip.type,
            name: SLIP_TYPE_LOOKUP[slip.type]
          },
          ta: {
            id: slip.TA_informed
          },
          ta_informed: {
            id: informed
          },
          trainees: slip.trainees.map(t => ({id: t})),
        }
      })
    case UPDATE_TRAINEE_VIEW:
      return Object.assign({}, state, {
        traineeView: action.traineeView,
        leaveSlip: {
          ...state.leaveSlip,
          ta: action.TA,
        },
        groupSlip: {
          ...state.groupSlip,
          ta: action.TA,
        },
      })
    case CHANGE_ROLL_FORM:
      return Object.assign({}, state, {
        rollStatus: action.values.rollStatus,
      })
    case RESET_ROLL_FORM:
      return Object.assign({}, state, {
        rollStatus: {}
      })
    case CHANGE_LEAVESLIP_FORM:
      return Object.assign({}, state, {
        leaveSlip: action.values
      })
    case RESET_LEAVESLIP_FORM:
      return Object.assign({}, state, {
          leaveSlip: {
            comment: "",
            slipType: {},
            ta: TA_EMPTY,
            ta_informed: TA_EMPTY,
            location: "",
            hostPhone: "",
            hostName: "",
            hcNotified: "",
          }
        })
    case CHANGE_GROUPSLIP_FORM:
      return Object.assign({}, state, {
        groupSlip: action.values
      })
    case RESET_GROUPSLIP_FORM:
      return Object.assign({}, state, {
        groupSlip: {
          comment: "",
          slipType: {},
          ta: TA_EMPTY,
          ta_informed: TA_EMPTY,
          trainees: []
        }
      })
    default:
      return state;
  }
}

function show(state=initialState.show, action) {
  switch (action.type) {
    case SHOW_CALENDAR:
      return action.value
    default:
      return state;
  }
}

function selectedEvents(state=[], action) {
  switch (action.type) {
    case EDIT_GROUP_LEAVESLIP:
    case EDIT_LEAVESLIP:
      return action.slip.events
    case CHANGE_LEAVESLIP_FORM:
    case CHANGE_ROLL_FORM:
      return action.values.selectedEvents
    case TOGGLE_EVENT:
      // if event is in state
      if(intersection(state, [action.event], (ev) => ev.id).length == 1) {
        return complement(state, [action.event], (ev) => ev.id)
      } else {
        return union(state, [action.event], (ev) => ev.id)
      }
    case DESELECT_ALL_EVENTS:
    case DESTROY_LEAVESLIP:
    case SUBMIT_ROLL:
    case SUBMIT_LEAVESLIP:
    case SUBMIT_GROUPSLIP:
    case RESET_LEAVESLIP_FORM:
    case RESET_GROUPSLIP_FORM:
      return [];
    default:
      return state;
  }
}

function leaveslips(state = initialState.leaveslips, action) {
  switch (action.type) {
    case UPDATE_ATTENDANCE:
      return action.attendance.individualslips
    case SUBMIT_LEAVESLIP:
      // remove old slips and update
      return [
        ...complement(state, action.leaveslips, slip => slip.id),
        ...action.leaveslips,
      ]
    case DESTROY_LEAVESLIP:
      return complement(state, action.slip, ls => ls.id)
    default:
      return state;
  }
}

function groupslips(state = initialState.groupslips, action) {
  switch (action.type) {
    case UPDATE_ATTENDANCE:
      return action.attendance.groupslips
    case SUBMIT_GROUPSLIP:
      return [
        ...complement(state, action.leaveslips, slip => slip.id),
        ...action.leaveslips,
      ]
    case DESTROY_GROUPSLIP:
      return complement(state, action.slip, ls => ls.id)
    default:
      return state;
  }
}

function events(state=initialState.events, action) {
  switch(action.type) {
    case UPDATE_EVENTS:
      return action.eventsView;
    default:
      return state;
  }
}

function showLegend(state=initialState.showLegend, action) {
  switch(action.type) {
    case TOGGLE_LEGEND:
      return !state
    default:
      return state
  }
}

const reducers = {
  //static variables that will never mutate
  groupevents: (state = {}) => state,
  trainee: (state = {}) => state,
  trainees: (state = {}) => state,
  tas: (state = {}) => state,
  term: (state = {}) => state,
  //these will mutate...
  submitting: (state = {}) => state,
  formSuccess: (state = {}) => state,

  // variables that will mutate
  showLegend,
  events,
  form,
  date,
  show,
  selectedEvents,
  rolls,
  leaveslips,
  groupslips,
}

const combined = combineReducers(reducers);

export default combined;
