import React, { Component } from 'react'
import { changeTraineeView } from '../actions'
import PropTypes from 'prop-types'
import Select from 'react-select'
import { isAM } from '../constants'
import * as yup from 'yup'

//client side validation
let modelSchema = (props) => {
  return yup.object({
    traineeView: yup.object().required("If you see this, something is wrong."),
  });
}

const customStyles = {
  option: (provided, state) => ({
    ...provided,
    color: state.isSelected ? "white" : "#434a54",
  }),
}

const TraineeSelector = (props) => {
  let schema = modelSchema(props);
  return (
    isAM(props.form.trainee) &&
      <div className="dt-roll__trainee-select">
        <b>Trainee</b>
        <Select styles={customStyles} name="traineeView" isClearable={false} options={props.form.trainees} getOptionLabel={({firstname, lastname}) => firstname + " " + lastname} getOptionValue={({id}) => id} value={props.form.traineeView} onChange={props.changeTraineeView} />
      </div>
    )
}

export default TraineeSelector
