import yup from 'yup'

import { TA_IS_INFORMED } from '../constants'

const nightFieldSchema = yup.mixed().when('slipType', {
  is: (val) => {
    return val.id == 'NIGHT'
  },
  then: yup.string().required('Please fill in all the fields for night/meal out'),
})

const mealFieldSchema = yup.mixed().when('slipType', {
  is: (val) => {
    return val.id == 'MEAL' || val.name == 'NIGHT'
  },
  then: yup.string().required('Please fill in all the fields for night/meal out'),
})

const taFieldSchema = yup.mixed().when('ta_informed', {
  is: (val) => {
    return val.id == TA_IS_INFORMED.id
  },
  then: yup.mixed().notOneOf([{}], "Please select a TA" )
})

const SlipSchema = {
  selectedEvents: yup.array().required("Please select an event for your leaveslip."),
  trainee: yup.object().required("If you see this, something is wrong."),
  slipType: yup.mixed().notOneOf([{}], "Please select a reason for your leaveslip."),
  ta_informed: yup.object(),
  ta: taFieldSchema,
  description: yup.string().required("Please enter a description for your leaveslip."),
  location: mealFieldSchema,
  hostName: mealFieldSchema,
  hostPhone: nightFieldSchema,
  hcNotified: nightFieldSchema,
}

export const LeaveSlipSchema = (props) => {
  return yup.object(SlipSchema);
}

export const GroupSlipSchema = (props) => {
  return yup.object({
    ...SlipSchema,
    trainees: yup.array().min(2, "Please select at least ${min} trainees"),
  })
}
