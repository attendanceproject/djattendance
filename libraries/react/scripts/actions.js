import {format, isWithinRange} from 'date-fns'

import { getDateDetails } from './selectors/selectors'
import { taInformedToServerFormat, TA_EMPTY } from './constants'

export const TOGGLE_LEGEND = 'TOGGLE_LEGEND'
export const toggleLegend = () => {
  return {
    type: TOGGLE_LEGEND
  }
}

export const selectPeriod = (period) => {
  return (dispatch, getState) => {
    let dateDetails = getDateDetails(getState())
    dispatch(changeDate((period - dateDetails.period) * 14))
  }
}

export const CHANGE_DATE = 'CHANGE_DATE'
export const changeDate = (days) => {
  return {
    type: CHANGE_DATE,
    days: days
  }
}

export const TOGGLE_EVENT = 'TOGGLE_EVENT'
export const toggleEvent = (ev) => {
  return (dispatch, getState) => {
    if (getState().show !='summary') {
      dispatch(toggle(ev))
    }
  }
}
const toggle = (ev) => {
  return {
    type: TOGGLE_EVENT,
    event: ev,
  }
}

export const DESELECT_ALL_EVENTS = 'DESELECT_ALL_EVENTS'
export const deselectAllEvents = () => {
  return {
    type: DESELECT_ALL_EVENTS
  };
}

export const FINALIZE_ROLL = 'FINALIZE_ROLL'
export const finalizeRoll = () => {
  return function(dispatch, getState) {
    let dateDetails = getDateDetails(getState())
    // rename the post data here to keep django api clean for future reuse
    dateDetails.trainee = getState().form.traineeView
    dateDetails.submitter = getState().trainee
    return $.ajax({
      url: '/attendance/api/rolls/finalize/',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(dateDetails),
      success: function(data, status, jqXHR) {
        dispatch(submitRoll(data.rolls))
        new Notification(Notification.SUCCESS, 'Finalized').show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Roll post error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    })
  }
}

export const postRollSlip = (rollSlip, selectedEvents, slipId) => {
  if ((rollSlip.rollStatus !== undefined || rollSlip.rollStatus != "") && (rollSlip.slipType === undefined || rollSlip.slipType == "")) {
    return function(dispatch) {
      dispatch(postRoll(rollSlip, selectedEvents));
    }
  } else if ((rollSlip.rollStatus === undefined || rollSlip.rollStatus == "") && (rollSlip.slipType !== undefined || rollSlip.slipType != "")) {
    return function(dispatch) {
      dispatch(postLeaveSlip(rollSlip, selectedEvents, slipId));
    }
  } else if ((rollSlip.rollStatus !== undefined || rollSlip.rollStatus != "") && (rollSlip.slipType !== undefined || rollSlip.slipType != "")) {
    return function(dispatch) {
      dispatch(postRoll(rollSlip, selectedEvents, slipId, true));
    }
  }
}

export const SUBMIT_ROLL = 'SUBMIT_ROLL'
export const submitRoll = (rolls) => {
  return {
    type: SUBMIT_ROLL,
    rolls: rolls
  }
}

export const RESET_ROLL_FORM = 'RESET_ROLL_FORM'
export const resetRollForm = () => {
  return {
    type: RESET_ROLL_FORM
  };
}

export const RESET_LEAVESLIP_FORM = 'RESET_LEAVESLIP_FORM'
export const resetLeaveslipForm = () => {
  return {
    type: RESET_LEAVESLIP_FORM
  };
}

export const RESET_GROUPSLIP_FORM = 'RESET_GROUPSLIP_FORM'
export const resetGroupslipForm = () => {
  return {
    type: RESET_GROUPSLIP_FORM
  };
}

export const postRoll = (values) => {
  var rolls = [];
  var roll = {
    "event": null,
    "trainee": values.traineeView.id,
    "status": values.rollStatus.id,
    "finalized": false,
    "notes": "",
    "submitted_by": values.trainee.id,
    "last_modified": Date.now(),
    "date": null
  }
  let selectedEvents = values.selectedEvents;
  for (var i = 0; i < selectedEvents.length; i++) {
    rolls.push(Object.assign({}, roll, {
      event: selectedEvents[i].id,
      date: format(selectedEvents[i].start_datetime, 'YYYY-MM-DD')
    }));
  }
  return function(dispatch) {
    var data = null;
    if (rolls.length == 1) {
      data = rolls[0];
    } else {
      data = JSON.stringify(rolls);
    }

    return $.ajax({
      url: '/api/rolls/',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(rolls),
      success: function(data, status, jqXHR) {
        dispatch(submitRoll(rolls));
        dispatch(resetRollForm());
        new Notification(Notification.SUCCESS, 'Saved').show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Roll post error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
  }
}

export const CHANGE_ROLL_FORM = 'CHANGE_ROLL_FORM'
export const changeRollForm = (values) => {
  return {
    type: CHANGE_ROLL_FORM,
    values: values,
  }
}

export const UPDATE_TRAINEE_VIEW = 'UPDATE_TRAINEE_VIEW'
export const updateTraineeView = (trainee, TA) => {
  return {
    type: UPDATE_TRAINEE_VIEW,
    traineeView: trainee,
    TA: TA,
  }
}

export const UPDATE_EVENTS = 'UPDATE_EVENTS'
export const updateEvents = (events) => {
  return {
    type: UPDATE_EVENTS,
    eventsView: events
  }
}

export const UPDATE_ATTENDANCE = 'UPDATE_ATTENDANCE'
export const updateAttendance = (attendance) => {
  return {
    type: UPDATE_ATTENDANCE,
    attendance: attendance
  }
}

export const CHANGE_TRAINEE_VIEW = 'CHANGE_TRAINEE_VIEW'
export const changeTraineeView = (trainee) => {
  return function(dispatch, getState) {
    dispatch(updateTraineeView(trainee, getState().tas.filter(ta => ta.id == trainee.TA)[0]))
    $.ajax({
      url: '/api/events',
      type: 'GET',
      data: {
        trainee: trainee.id
      },
      success: function(data, status, xhr) {
        dispatch(deselectAllEvents())
        dispatch(updateEvents(data))
      },
      error: function(xhr, status, error) {
        console.log('events error')
        console.log(xhr, status, error);
      }
    })

    $.ajax({
      url: '/api/attendance',
      type: 'GET',
      data: {
        trainee: trainee.id
      },
      success: function(data, status, xhr) {
        // this returns a list of trainees so just grab the first
        dispatch(updateAttendance(data[0]))
      },
      error: function(xhr, status, error) {
        console.log('attendance error')
        console.log(xhr, status, error)
      }
    })
  }
}

export const duplicateSlip = (values) => {
  let type = CHANGE_LEAVESLIP_FORM
  if (values.classname == 'group') {
    type = CHANGE_GROUPSLIP_FORM
  }
  return {
    type: type,
    values: {
      ...values,
      id: undefined,
    }
  }
}

export const CHANGE_LEAVESLIP_FORM = 'CHANGE_LEAVESLIP_FORM'
export const changeLeaveSlipForm = (values) => {
  return {
    type: CHANGE_LEAVESLIP_FORM,
    values: values
  }
}

export const CHANGE_GROUPSLIP_FORM = 'CHANGE_GROUPSLIP_FORM'
  //values here is all the values of the form
export const changeGroupSlipForm = (values) => {
  return {
    type: CHANGE_GROUPSLIP_FORM,
    values: values
  }
}

export const SUBMIT_LEAVESLIP = 'SUBMIT_LEAVESLIP'
export const submitLeaveSlip = (slip) => {
  return {
    type: SUBMIT_LEAVESLIP,
    leaveslips: Array.isArray(slip) ? slip : [slip],
  }
}

export const postLeaveSlip = (values) => {
  var event_details = values.selectedEvents.map(e => ({
    id: e.id,
    date: format(e.start_datetime, 'YYYY-MM-DD'),
    name: e.name,
    code: e.code,
  }))
  let TA_informed = values.ta.id == TA_EMPTY.id ? undefined : values.ta.id;
  var slip = {
    "type": values.slipType.id,
    "status": "P",
    "TA_informed": TA_informed,
    "TA": values.traineeView.TA,
    "trainee": values.traineeView.id,
    "submitted": Date.now(),
    "last_modified": Date.now(),
    "finalized": null,
    "description": values.description,
    "comments": values.comments,
    "events": event_details,
    "location": values.location,
    "host_name": values.hostName,
    "host_phone": values.hostPhone,
    "hc_notified": values.hcNotified,
    ...taInformedToServerFormat(values.ta_informed),
  };

  return (dispatch, getState) => {
    let slipId = getState().form.leaveSlip.id || null
    slip.id = slipId
    return $.ajax({
      url: '/api/individualslips/',
      type: slipId ? 'PUT' : 'POST',
      contentType: 'application/json',
      data: JSON.stringify(slipId ? [slip] : slip),
      success: function(data, status, jqXHR) {
        console.log("returned data", data, status, jqXHR);
        dispatch(submitLeaveSlip(data));
        dispatch(resetLeaveslipForm());
        new Notification(Notification.SUCCESS, 'Saved').show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Slip post error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
  }
}

//using destroy because delete is an official HTTP action and is used for the thunk
export const DESTROY_LEAVESLIP = 'DESTROY_LEAVESLIP'
export const destroyLeaveSlip = (slip) => {
  return {
    type: DESTROY_LEAVESLIP,
    slip: Array.isArray(slip) ? slip : [slip],
  }
}

export const EDIT_LEAVESLIP = 'EDIT_LEAVESLIP'
export const loadLeaveSlip = (slip) => {
  return {
    type: EDIT_LEAVESLIP,
    slip: slip,
  }
}

export const editLeaveSlip = (slip) => {
  return (dispatch, getState) => {
    dispatch(selectTab(2))
    dispatch(deselectAllEvents())
    dispatch(loadLeaveSlip(slip))
    // Assumed that only leaveslips for this period is selected only check
    // for week difference
    let dateDetails = getDateDetails(getState())
    slip.events.sort((a, b) =>{
      return a.start_datetime - b.start_datetime
    })
    if (!isWithinRange(slip.events[0].start_datetime, dateDetails.weekStart, dateDetails.weekEnd)) {
      dateDetails.isFirst ? dispatch(changeDate(7)) : dispatch(changeDate(-7))
    }
  }
}

export const EDIT_GROUP_LEAVESLIP = 'EDIT_GROUP_LEAVESLIP'
export const loadGroupSlip = (slip) => {
  return {
    type: EDIT_GROUP_LEAVESLIP,
    slip: slip
  }
}

export const editGroupLeaveSlip = (slip) => {
  return (dispatch, getState) => {
    dispatch(selectTab(3))
    slip.events = getState().groupevents.filter(e => e.start_datetime >= slip.start && e.end_datetime <= slip.end)
    dispatch(loadGroupSlip(slip))
    // Assumed that only leaveslips for this period is selected only check
    // for week difference
    let dateDetails = getDateDetails(getState())
    if (!isWithinRange(slip.start, dateDetails.weekStart, dateDetails.weekEnd)) {
      dateDetails.isFirst ? dispatch(changeDate(7)) : dispatch(changeDate(-7))
    }
  }
}

export const deleteLeaveSlip = (slip) => {
  return function(dispatch) {
    dispatch(showCalendar(0));
    dispatch(destroyLeaveSlip(slip));
    return $.ajax({
      url: '/api/individualslips/' + slip.id.toString(),
      type: 'DELETE',
      success: function(data, status, jqXHR) {
        new Notification(Notification.SUCCESS, "Leave slip deleted!").show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Slip delete error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
  }
}

export const SUBMIT_GROUPSLIP = 'SUBMIT_GROUPSLIP'
export const submitGroupSlip = (gSlip) => {
  return {
    type: SUBMIT_GROUPSLIP,
    leaveslips: Array.isArray(gSlip) ? gSlip : [gSlip],
  }
}

export const postGroupSlip = (gSlip) => {
  // Group slips are assigned to a trainee by time range, so cannot skip events in the middle.
  gSlip.start = gSlip.selectedEvents[0].start_datetime
  gSlip.end = gSlip.selectedEvents[0].end_datetime
  for (var i = 1; i < gSlip.selectedEvents.length; i++) {
    let event = gSlip.selectedEvents[i];
    if (event.start_datetime < gSlip.start) {
      gSlip.start = event.start_datetime;
    }
    if (event.end_datetime > gSlip.end) {
      gSlip.end = event.end_datetime;
    }
  }
  let TA_informed = gSlip.ta.id == TA_EMPTY.id ? undefined : gSlip.ta.id;
  var slip = {
    "type": gSlip.slipType.id,
    "status": "P",
    "submitted": Date.now(),
    "last_modified": Date.now(),
    "finalized": null,
    "description": gSlip.description,
    "comments": gSlip.comments,
    "start": gSlip.start,
    "end": gSlip.end,
    "TA": gSlip.traineeView.TA,
    "TA_informed": TA_informed,
    "trainee": gSlip.traineeView.id,
    "trainees": gSlip.trainees.map(t => t.id),
    ...taInformedToServerFormat(gSlip.ta_informed),
  }

  return function(dispatch, getState) {
    let slipId = getState().form.groupSlip.id || null
    slip.id = slipId
    return $.ajax({
      url: '/api/groupslips/',
      type: slipId ? 'PUT' : 'POST',
      contentType: 'application/json',
      data: JSON.stringify(slipId ? [slip] : slip),
      success: function(data, status, jqXHR) {
        // only add the groupslip to display if the trainee is in it
        if (slip.trainees.indexOf(getState().form.traineeView.id) >= 0) {
          dispatch(submitGroupSlip(data));
        }
        dispatch(resetGroupslipForm());
        new Notification(Notification.SUCCESS, 'Saved').show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Slip post error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
  }
}

export const DESTROY_GROUPSLIP = 'DESTROY_GROUPSLIP'
export const destroyGroupSlip = (slip) => {
  return {
    type: DESTROY_GROUPSLIP,
    slip: Array.isArray(slip) ? slip : [slip],
  }
}

export const deleteGroupSlip = (slip) => {
  return function(dispatch) {
    dispatch(showCalendar(0));
    dispatch(destroyGroupSlip(slip));
    return $.ajax({
      url: '/api/groupslips/' + slip.id.toString(),
      type: 'DELETE',
      success: function(data, status, jqXHR) {
        new Notification(Notification.SUCCESS, "Group slip deleted!").show();
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log('Slip delete error!');
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
  }
}

export const SELECT_TAB = 'SELECT_TAB'
export const selectTab = (index) => {
  return function(dispatch, getState) {
    let show = getState().show
    // deselect events if going to and from the group slip tab. Reset the forms.
    if ((show!=='groupslip' && index===3) || (show==='groupslip' && index!==3)) {
      dispatch(resetGroupslipForm())
      dispatch(resetLeaveslipForm())
      dispatch(resetRollForm())
      dispatch(deselectAllEvents())
    }
    dispatch(showCalendar(index))
  }
}

export const SHOW_CALENDAR = 'SHOW_CALENDAR'
export const showCalendar = (index) => {
  switch (index) {
    case 0:
      return {
        type: SHOW_CALENDAR,
        value: 'summary'
      }
    case 1:
      return {
        type: SHOW_CALENDAR,
        value: 'roll'
      }
    case 2:
      return {
        type: SHOW_CALENDAR,
        value: 'leaveslip'
      }
    case 3:
      return {
        type: SHOW_CALENDAR,
        value: 'groupslip'
      }
  }
}
