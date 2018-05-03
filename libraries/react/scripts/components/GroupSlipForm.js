import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Button, Collapse, OverlayTrigger, Popover } from 'react-bootstrap'
import Form from 'react-formal'
import types from 'react-formal-inputs'
import yup from 'yup'

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
import SubmitButton from './SubmitButton'

Form.addInputTypes(types)

window.addTrainees = (trainee_ids) => {
  let prev_trainees = store.getState().form.groupSlip.trainees.filter((t) => trainee_ids.indexOf(t.id) < 0).map((t) => t.id);
  trainee_ids += prev_trainees;
  let trainees = store.getState().trainees.filter((t) => trainee_ids.indexOf(t.id) >= 0);
  store.dispatch(changeGroupSlipForm(
    {
      ...store.getState().form.groupSlip,
      trainees: trainees,
    }
  ));
}

const GroupSlipForm = ({...props}) => {
  let schema = GroupSlipSchema(props);
  return (
    <div className="dt-leaveslip">
      <SlipTitle {...props} />
      <TAComments comments={props.form.comments} />
      <Form
        schema={schema}
        value={props.form}
        onChange={props.changeGroupSlipForm}
        onSubmit={props.postGroupSlip}
        delay={100}
      >
        <b>Select Trainees</b>
        <Form.Field type='multiSelect' data={props.trainees} name='trainees' valueField='id' textField='name' className='dt-leaveslip__trainees' />
        <button type="button" className="btn btn-primary dt-leaveslip__trainee-group" data-toggle="modal" data-target="#trainee_select">Add Trainee Group</button>
        <SelectedEventsField />

        <SlipTypesField slipTypes={GROUP_SLIP_TYPES} lastSlips={[]} />

        <h4 className='dt-leaveslip__title'>Description</h4>
        <Form.Field type='textarea' name='description' className='dt-leaveslip__description'/>
        <TAInformedField taInformed={props.form.ta_informed} tas={props.tas} />
        <FormSummary />
        <LeaveSlipNote />
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
