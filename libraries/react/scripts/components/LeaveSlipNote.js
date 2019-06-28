import React from 'react'
import { Button, Alert } from 'react-bootstrap'

const LeaveSlipNote = (props) => (
  <Alert bsStyle="info" className="dt-leaveslip__note">
    <b>Meal sign out:</b> If your leave of absence permits you to miss a meal, <u>you must also</u> sign out on the appropriate meal sign-out sheet.
    <br/>
    <br/>
    <b>Service scheduling:</b> If your leave of absence permits you to be out of the schedule for seven days or more, <u>you must also</u> submit a note to the service scheduling mail slot.
  </Alert>
)

export default LeaveSlipNote
