import { connect } from 'react-redux'
import { postRoll, changeTraineeView, changeRollForm, finalizeRoll } from '../actions'
import { getDateDetails } from '../selectors/selectors.js'
import { canFinalizeRolls, canSubmitRoll, isWeekFinalized } from '../constants.js'
import RollForm from '../components/RollForm'
import { isAM } from '../constants'

const mapStateToProps = (state) => {
  let dateDetails = getDateDetails(state)
  return {
    form: {
      selectedEvents: state.selectedEvents,
      rollStatus: state.form.rollStatus,
      trainee: state.form.traineeView,
      trainees: state.trainees,
      traineeView: state.form.traineeView,
    },
    canFinalizeWeek: canFinalizeRolls(state.term, state.date, state.finalizedweeks) ||  isAM(state.trainee),
    canSubmitRoll: canSubmitRoll(dateDetails) ||  isAM(state.trainee),
    isWeekFinalized: isWeekFinalized(state.term, state.date, state.finalizedweeks),
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    postRoll: (values) => { dispatch(postRoll(values)) },
    changeTraineeView: (values) => { dispatch(changeTraineeView(values)) },
    changeRollForm: (values) => { dispatch(changeRollForm(values)) },
    finalizeRoll: () => { dispatch(finalizeRoll()) }
  }
}

const RollPane = connect(
  mapStateToProps,
  mapDispatchToProps
)(RollForm)

export default RollPane
