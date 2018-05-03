import React, { Component } from 'react'
import { Alert, Button } from 'react-bootstrap'

import SlipDetail from './SlipDetail'
import { FA_ICON_LOOKUP } from '../constants'

const Summary = (p) => {
  let eventsWithRolls = p.eventsRolls.filter(esr => esr.event.roll)
  let unexcused_absences = eventsWithRolls.filter(esr => esr.event.roll.status === 'A' && esr.event.status.slip !== 'approved')
  let unexcused_tardies = eventsWithRolls.filter(esr => (['T', 'U', 'L'].includes(esr.event.roll.status) && esr.event.status.slip !== 'approved'))
  let excused_absences = eventsWithRolls.filter(esr => esr.event.roll.status === 'A' && esr.event.status.slip === 'approved')
  let excused_tardies = eventsWithRolls.filter(esr => (['T', 'U', 'L'].includes(esr.event.roll.status) && esr.event.status.slip === 'approved'))
  const TARDY_LIMIT = 4
  const ABSENT_LIMIT = 1
  let tardies = unexcused_tardies.length
  let absences = unexcused_absences.length
  let tardyLifestudies = tardies > TARDY_LIMIT  ? tardies - TARDY_LIMIT + 1 : 0
  let absentLifestudies = absences > ABSENT_LIMIT ? absences - ABSENT_LIMIT + 1 : 0

  return (
    <div>
      <h5 className="summary__lifestudies">
        LIFE STUDIES POSSIBLE: {tardyLifestudies + absentLifestudies}
      </h5>
      <div className="row summary__attendance">
        <div className="col-xs-5">Unexcused Absences</div>
        <div className="col-xs-1">{absences}</div>
        <div className="col-xs-5">Excused Absences</div>
        <div className="col-xs-1">{excused_absences.length}</div>
        <div className="col-xs-5">Unexcused Tardies</div>
        <div className="col-xs-1">{tardies}</div>
        <div className="col-xs-5">Excused Tardies</div>
        <div className="col-xs-1">{excused_tardies.length}</div>
      </div>

      {
        p.leaveslips.length ? <div>
        <h5>Individual Leave Slips: {p.leaveslips.length}</h5>
        <div className="row summary__leaveslips">
          <div className="col-xs-2">Submitted</div>
          <div className="col-xs-1">State</div>
          <div className="col-xs-6">Event</div>
          <div className="col-xs-2">Reason</div>
        </div>
        {p.leaveslips.sort((s1, s2) => s1.submitted > s2.submitted ? -1 : 1)
          .map((slip, i) => <SlipDetail slip={slip} key={i} onClick={() => p.editSlip(slip)} deleteSlip={p.deleteSlip} /> )}
        </div> : ''
      }

      {
        p.groupslips.length ? <div>
        <h5>Group Leave Slips: {p.groupslips.length}</h5>
        <div className="row summary__leaveslips">
          <div className="col-xs-2">Submitted</div>
          <div className="col-xs-1">State</div>
          <div className="col-xs-6">Time</div>
          <div className="col-xs-2">Reason</div>
        </div>
        {p.groupslips.sort((s1, s2) => s1.submitted > s2.submitted ? -1 :1)
          .map((slip, i) => <SlipDetail trainee={p.trainee} slip={slip} key={i} onClick={() => p.editGroupSlip(slip)} deleteSlip={p.deleteGroupSlip} /> )}
        </div> : ''
      }

      <Alert bsStyle="danger" className="dt-leaveslip__note">
        Note: Report information will not be up-to-date until attendance office hours (i.e., when the potential violators list is posted).
      </Alert>
    </div>
  )
}

Summary.propTypes = {
}

export default Summary
