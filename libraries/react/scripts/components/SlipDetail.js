import React, { Component } from 'react'
import { format } from 'date-fns'
import { Button } from 'react-bootstrap'

import SlipStatusIcon from './SlipStatusIcon'

let dateFormat = 'M/D/YY'
let datetimeFormat = 'M/D/YY h:mm a'

const SlipDetail = ({ slip, deleteSlip, onClick }) => {
  let click = () => onClick(slip)
  let isUnfinalized = '--unfinalized'
  return (
  <div className={"row summary__leaveslips-row" + isUnfinalized} onClick={() => click(slip)}>
    <div className="col-xs-2">{format(new Date(slip.submitted), dateFormat)}</div>
    <div className="col-xs-1"><SlipStatusIcon status={slip.status} /></div>
    <div className="col-xs-6">
      {
        slip.classname == 'individual' ? slip.events.map(e =>
          e.name + ' ' + format(moment(e.date), dateFormat)
        ).join(', ') :
        format(new Date(slip.start), datetimeFormat) + ' to ' + format(new Date(slip.end), datetimeFormat)
      }
    </div>
    <div className="col-xs-1">{slip.type.charAt(0).toUpperCase() + slip.type.slice(1).toLowerCase()}</div>
    <div className="col-xs-1 col-xs-offset-1">
    </div>
  </div>
  )
}

export default SlipDetail
