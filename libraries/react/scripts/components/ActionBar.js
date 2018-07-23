import React from 'react'
import PropTypes from 'prop-types'
import { Tabs, Tab, Button, Collapse, OverlayTrigger, Popover } from 'react-bootstrap'

import SummaryPane from '../containers/SummaryPane'
import RollPane from '../containers/RollPane'
import LeaveSlipPane from '../containers/LeaveSlipPane'
import GroupSlipPane from '../containers/GroupSlipPane'
import TraineeSelectorContainer from '../containers/TraineeSelectorContainer'
import { isAM } from '../constants'

const ActionBar = ({show, trainee, onSelectTab, traineeView}) => {
  return (
    <div className="dt">
      <h2 className="dt__actionbar-heading">View Personal Attendance</h2>
        { isAM(trainee) ?
          <TraineeSelectorContainer />
          : ''
        }
      <Tabs activeKey={["summary", "roll", "leaveslip", "groupslip"].indexOf(show)} animation={false} id="noanim-tab-example" onSelect={onSelectTab}>
        <Tab eventKey={0} title="Summary">
          <SummaryPane />
        </Tab>
        {trainee.self_attendance || isAM(trainee) ?
          <Tab eventKey={1} title="Roll">
            <RollPane />
          </Tab>
          : '' }
        <Tab eventKey={2} title="Personal Slips">
          <LeaveSlipPane />
        </Tab>
        <Tab eventKey={3} title="Group Slips">
          <GroupSlipPane />
        </Tab>
      </Tabs>
    </div>
  )
}

ActionBar.propTypes = {
  // submitRoll: PropTypes.bool.isRequired,
  // submitLeaveSlip: PropTypes.bool.isRequired,
  // submitGroupLeaveSlipShow: PropTypes.bool.isRequired,
  // selectedEvents: PropTypes.arrayOf(PropTypes.object.isRequired).isRequired,
  // toggleSubmitRoll: PropTypes.func.isRequired,
  // toggleSubmitLeaveSlip: PropTypes.func.isRequired,
  // toggleSubmitGroupSlip: PropTypes.func.isRequired
  // showCalendar: PropTypes.func.isRequired
}

export default ActionBar
