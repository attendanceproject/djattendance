import React, { Component } from 'react'
import { Button } from 'react-bootstrap'
import { ATTENDANCE_MONITOR_GROUP } from '../constants'

const SlipTitle = (props) => {
  let isAM = props.trainee.groups.indexOf(ATTENDANCE_MONITOR_GROUP) >= 0
  let isSubmitter = props.trainee.id == props.form.trainee
  let actionText
  if (!props.form.id) {
    actionText = 'Submit'
  } else if (props.form.finalized) {
    actionText = 'View'
  } else {
    actionText = 'Edit'
  }
  return (
    <h4 className='dt-leaveslip__title'>
      {actionText + ' Leave Slip'}&nbsp;
      {props.form.id && <a onClick={props.resetForm} className="dt-leaveslip__title__close pull-right"><i className="fa fa-close"></i></a>}
      {props.form.id && <Button onClick={() => props.duplicateSlip(props.form)} className="pull-right dt-leaveslip__title__button" bsSize="small">Duplicate Slip</Button>}
      {props.form.id && (isAM || (!props.form.finalized && isSubmitter)) &&
        <Button className="dt-leaveslip__title__button pull-right" bsSize="xsmall" bsStyle="danger"
          onClick={(e) => {
            if (confirm('Are you sure you want to delete this leave slip?')) {
              props.deleteSlip(props.form)
            }
            e.stopPropagation()
          }}
        >
          Delete Slip
        </Button>
      }
    </h4>
  )
}

export default SlipTitle
