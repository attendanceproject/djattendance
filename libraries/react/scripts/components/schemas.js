import * as yup from 'yup'

import { TA_IS_INFORMED, TA_EMPTY} from '../constants'

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

const taFieldSchema = yup.mixed().when('informed', {
  is: (val) => {
    return val.id == TA_IS_INFORMED.id
  },
  then: yup.mixed().notOneOf([TA_EMPTY], "Please select a TA" )
})

const SlipSchema = {
  selectedEvents: yup.array().required("Please select an event for your leave slip."),
  trainee: yup.object().required("If you see this, something is wrong."),
  slipType: yup.mixed().notOneOf([{}], "Please select a reason for your leave slip."),
  informed: yup.object().notOneOf([TA_EMPTY], "Please select whether you have informed the training office."),
  taInformed: taFieldSchema,
  description: yup.string().required("Please enter a description for your leave slip."),
  location: mealFieldSchema,
  hostName: mealFieldSchema,
  hostPhone: nightFieldSchema,
  hcNotified: nightFieldSchema,
  // TA fields
  taAssigned: yup.object().notOneOf([TA_EMPTY], "Please select a TA to assign to this leave slip."),
  taComments: yup.string(),
  privateComments: yup.string(),
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
