import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Button, OverlayTrigger, Popover } from 'react-bootstrap'

import { ATTENDANCE_STATUS_LOOKUP, SLIP_STATUS_LOOKUP, FA_ICON_LOOKUP, joinValidClasses } from '../constants'

import { differenceInMinutes, subHours, getHours, getMinutes } from 'date-fns'

const EventView = ({ event, status, onClick, selected }) => {
  var todayClass = (event.id === 'TODAY') ? 'today-marker' : '';

  const START_TIME = 6
  const PIXELS_PER_MINUTE = 2/3
  const MIN_HEIGHT = 12
  let datetime = subHours(event.start_datetime, START_TIME)
  let minutes = getMinutes(datetime) + getHours(datetime)*60
  var divStyle = {
    top: minutes * PIXELS_PER_MINUTE + 25,
    height: Math.max(differenceInMinutes(event.end_datetime, event.start_datetime) * PIXELS_PER_MINUTE, MIN_HEIGHT),
    opacity: selected ? 0.5 : 1,
  };

  let formatDate = date => new Date(date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  let formatText = text => text.charAt(0).toUpperCase() + text.slice(1);

  // replace "-" in css class e.g. left-class with human-friendly " "
  let roll = event.roll
  var rollStatus = (roll ? ATTENDANCE_STATUS_LOOKUP[roll.status] : '').replace('-', ' ')
  var rollPopover = rollStatus ? 'Roll: ' + formatText(rollStatus) : '';
  var slipPopover = status.slip ? 'Slip: ' + formatText(status.slip) : '';
  var timePopover = formatDate(event.start_datetime) + ' - ' + formatDate(event.end_datetime);
  var namePopover = event.name;
  var faClasses = "fa fa-" + FA_ICON_LOOKUP[status.slip]
  var rollClasses = joinValidClasses([status.slip , status.roll, (selected ? 'selected' : ''), todayClass, 'cal-day__event'])

  let eventView = (
    <div className={rollClasses} style={divStyle} onClick={onClick}>
      {event.code}
      <div className={joinValidClasses(['slip', status.slip])}><i className={faClasses} aria-hidden="true"></i></div>
    </div>
  )
  return (
    <OverlayTrigger overlay={
      <Popover id={event.id + '-popover'}>
        {rollPopover}
        {rollPopover ? <br/> : ""}
        {slipPopover}
        {slipPopover ? <br/> : ""}
        {namePopover}
        <br/>
        {timePopover}
      </Popover>
      }>
      {eventView}
    </OverlayTrigger>
  )
}

EventView.propTypes = {
  // event: PropTypes.object.isRequired,
  // roll: PropTypes.object.isRequired,
  // slip: PropTypes.object.isRequired,
  // onClick: PropTypes.func.isRequired
}

export default EventView
