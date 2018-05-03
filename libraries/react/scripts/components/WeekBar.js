import React from 'react'
import PropTypes from 'prop-types'
import { format } from 'date-fns'
import Select from 'react-select';

import SlipStatusIcon from './SlipStatusIcon'

const WeekBar = ({isFirst, firstStart, firstEnd, secondStart, secondEnd, period, currentPeriod, showLegend,
                    onPrevWeek, onNextWeek, traineeView, selectPeriod, toggleLegend}) =>
{
  let periodChoices = Array.from(Array(10).keys()).map(c => { return {value: c, label: c}})
  let selectedPeriod = {value: period, label: period}
  return (
    <div className="col-md-12">
      <div className="row">
        <div className="col-xs-offset-1 col-md-11 weekbar-container">
          <div className="weekbar">
            <div className="row">
              <div className="weekbar__title no-padding col-md-5">
                WEEK {period * 2 + (isFirst ? 0 : 1)}&nbsp;
                PERIOD <Select className="weekbar__period" clearable={false} options={periodChoices} value={selectedPeriod} onChange={selectPeriod}/>
              </div>
              <div className="col-md-7">
                <div className="legend row">
                  <div className="tardy legend__tardy col-xs-4">Tardy</div>
                  <div className="absent legend__absent col-xs-4">Absent</div>
                  <div className="excused legend__excused col-xs-4">Excused</div>
                  <div className="approved tardy legend__approved col-xs-4">Excused Tardy</div>
                  <div className="approved absent legend__absent col-xs-4">Excused Absence</div>
                  <div className="pending legend__tardy col-xs-4">Pending</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-xs-offset-1 col-md-11 no-padding">
          <div className="weekbar-sub nav-tabs">
            <div className="btn-toolbar" role="toolbar">
              <div className="btn-group">
                <button className="weekbar-sub__date-range btn btn-default" disabled={isFirst} onClick={onPrevWeek}>
                  {format(firstStart, 'M/D')} - {format(firstEnd, 'M/D')}
                </button>
                <button className="weekbar-sub__date-range btn btn-default" disabled={!isFirst} onClick={onNextWeek}>
                  {format(secondStart, 'M/D')} - {format(secondEnd, 'M/D')}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

WeekBar.propTypes = {
  isFirst: PropTypes.bool.isRequired,
  onPrevWeek: PropTypes.func.isRequired,
  onNextWeek: PropTypes.func.isRequired,
};

export default WeekBar
