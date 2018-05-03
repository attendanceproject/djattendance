import React, { Component } from 'react'

import { FA_ICON_LOOKUP, SLIP_STATUS_LOOKUP } from '../constants'

const SlipStatusIcon = (props) => {
  let s = SLIP_STATUS_LOOKUP[props.status]
  return (
    <i className={" slip-status fa fa-" + FA_ICON_LOOKUP[s]} aria-hidden="true"></i>
  )
}

export default SlipStatusIcon
