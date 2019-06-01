import { connect } from 'react-redux'
import { deleteLeaveSlip, editLeaveSlip, editGroupLeaveSlip, deleteGroupSlip } from '../actions'
import { getGroupSlipsforPeriod, getLeaveSlipsforPeriod, getEventsByRollStatus, isTA } from '../selectors/selectors'
import Summary from '../components/Summary'

const mapStateToProps = (state) => {
  return {
    eventsRolls: getEventsByRollStatus(state),
    groupslips: getGroupSlipsforPeriod(state),
    leaveslips: getLeaveSlipsforPeriod(state),
    isTA: isTA(state),
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    deleteSlip: (slip) => {
      dispatch(deleteLeaveSlip(slip))
    },
    deleteGroupSlip: (slip) => {
      dispatch(deleteGroupSlip(slip))
    },
    editSlip: (slip) => {
      dispatch(editLeaveSlip(slip))
    },
    editGroupSlip: (slip) => {
      dispatch(editGroupLeaveSlip(slip))
    },
  }
}

const SummaryPane = connect(
  mapStateToProps,
  mapDispatchToProps
)(Summary)

export default SummaryPane
