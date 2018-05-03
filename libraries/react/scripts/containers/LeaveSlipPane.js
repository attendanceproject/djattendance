import { connect } from 'react-redux'
import { postLeaveSlip, changeLeaveSlipForm, resetLeaveslipForm, duplicateSlip, deleteLeaveSlip } from '../actions'
import { lastLeaveslips } from '../selectors/selectors'
import LeaveSlipForm from '../components/LeaveSlipForm'

const mapStateToProps = (state) => {
  return {
    lastSlips: lastLeaveslips(state),
    form: {
      ...state.form.leaveSlip,
      selectedEvents: state.selectedEvents,
      trainee: state.trainee,
      traineeView: state.form.traineeView
    },
    tas: state.tas,
    trainee: state.trainee,
  }
}
const mapDispatchToProps = (dispatch) => {
  return {
    postLeaveSlip: (values) => { dispatch(postLeaveSlip(values)) },
    changeLeaveSlipForm: (values) => { dispatch(changeLeaveSlipForm(values)) },
    resetForm: () => { dispatch(resetLeaveslipForm()) },
    duplicateSlip: (values) => { dispatch(duplicateSlip(values)) },
    deleteSlip: (slip) => { dispatch(deleteLeaveSlip(slip)) },
  }
}

const LeaveSlipPane = connect(
  mapStateToProps,
  mapDispatchToProps
)(LeaveSlipForm)

export default LeaveSlipPane
