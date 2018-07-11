import { connect } from 'react-redux'
import { changeDate, selectPeriod, toggleLegend } from '../actions'
import { getDateDetails } from '../selectors/selectors'
import WeekBar from '../components/WeekBar'

const mapStateToProps = (state) => {
  let details = getDateDetails(state)
  return {
    ...details,
    showLegend: state.showLegend,
    traineeView: state.form.traineeView,
    disablePeriodSelect: state.disablePeriodSelect,
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    onPrevWeek: () => {
      dispatch(changeDate(-7))
    },
    onNextWeek: () => {
      dispatch(changeDate(7))
    },
    selectPeriod: (period) => {
      dispatch(selectPeriod(period.value))
    },
    toggleLegend: () => {
      dispatch(toggleLegend())
    }
  }
}

const WeekNav = connect(
  mapStateToProps,
  mapDispatchToProps,
)(WeekBar)

export default WeekNav
