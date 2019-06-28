import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Alert, Button, Collapse, OverlayTrigger, Popover } from 'react-bootstrap'
import Form from 'react-formal'
import types from 'react-formal-inputs'

import { GROUP_SLIP_TYPES, INFORMED } from '../constants'
import { changeGroupSlipForm } from '../actions'
import { GroupSlipSchema } from './schemas'
import LeaveSlipNote from './LeaveSlipNote'
import SelectedEventsField from './SelectedEventsField'
import TAInformedField from './TAInformedField'
import FormSummary from './FormSummary'
import SlipTypesField from './SlipTypesField'
import SlipTitle from './SlipTitle'
import TAComments from './TAComments'
import TALabels from './TALabels'
import SubmitButton from './SubmitButton'

Form.addInputTypes(types)

window.addTrainees = (traineeIds) => {
  let prevTrainees = store.getState().form.groupSlip.trainees.filter((t) => traineeIds.indexOf(t.id) < 0).map((t) => t.id);
  traineeIds += prevTrainees;
  let trainees = store.getState().trainees.filter((t) => traineeIds.indexOf(t.id) >= 0);
  store.dispatch(changeGroupSlipForm(
    {
      ...store.getState().form.groupSlip,
      trainees: trainees,
    }
  ));
}

const GroupSlipForm = ({...props}) => {
  let schema = GroupSlipSchema(props);
  let highlightSubmitter = ({ item }) => {
    if (item.name == props.groupslip.submitter_name) {
      return (
        <span>
          <span style={{visibility: 'hidden'}}>{item.name}</span>
          <span style={{backgroundColor: '#FFDB77', padding: '0 .35em', position: 'absolute', right: '.35em'}}>
            <strong>{item.name}</strong>
          </span>
        </span>
      )
    } else {
      return (
        <span>{item.name}</span>
      )
    }
  }
  return (
    <div className="dt-leaveslip">

    <div>
      <Alert bsStyle="notice" className="dt-leaveslip__note">
        *Please note: Multiple group slips maybe submitted if there are one or more events that should not be covered in between the first and last events covered by the slip. (Due to different personal schedules, group slips automatically include everything from the first event to the last event selected.)
      </Alert>
    </div>

      <SlipTitle {...props} />
      {isTAView ? '' : <TAComments comments={props.form.comments} />}
      {isTAView ? <TALabels {...props.groupslip} /> : ''}
      <Form
        schema={schema}
        value={props.form}
        onChange={props.changeGroupSlipForm}
        onSubmit={props.postGroupSlip}
        delay={100}
      >
        <b>Trainees</b><b className="dt-leaveslip__submitter">Submitter: {props.groupslip.submitter_name}</b>
        <Form.Field type='multiSelect' data={props.trainees} tagComponent={highlightSubmitter} name='trainees' valueField='id' textField='name' className='dt-leaveslip__trainees' />
        {isTAView ? '' : <button type="button" className="btn btn-primary dt-leaveslip__trainee-group" data-toggle="modal" data-target="#trainee_select">Add Trainee Group</button>}
        <SelectedEventsField />

        <SlipTypesField slipTypes={GROUP_SLIP_TYPES} lastSlips={[]} />

        <h4 className='dt-leaveslip__title'>Description</h4>
        <Form.Field type='textarea' name='description' className='dt-leaveslip__description'/>

        {isTAView ?
          <div>
            <h4 className='dt-leaveslip__title'>TA comments</h4>
            <Form.Field type='textarea' name='taComments' className='dt-leaveslip__description'/>
          </div>
          :
          ''
        }
        <TAInformedField informed={props.form.informed} tas={props.tas} />
        {isTAView ?
          <div>
            <h4 className='dt-leaveslip__title'>TA Assigned to this leaveslip:</h4>
            <Form.Field type='DropdownList' data={props.tas} name='taAssigned' className="dt-leaveslip__ta-list" valueField='id' textField='name' />
          </div>
          :
          ''
        }
        {isTAView ?
          <div>
            <h4 className='dt-leaveslip__title'>Private TA comments</h4>
            <Form.Field type='textarea' name='privateComments' className='dt-leaveslip__description'/>
          </div>
          :
          ''
        }
        <FormSummary />
        {isTAView ? '' : <LeaveSlipNote />}
        <SubmitButton finalized={props.form.finalized} />
      </Form>
    </div>
  )
}


GroupSlipForm.propTypes = {
  // fields: PropTypes.object.isRequired,
  // handleSubmit: PropTypes.func.isRequired,
  // resetForm: PropTypes.func.isRequired,
  // submitting: PropTypes.bool.isRequired,
  // post: PropTypes.func.isRequired,
  // toggleOtherReasons: PropTypes.func.isRequired
}
export default GroupSlipForm;
