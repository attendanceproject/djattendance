import React from 'react'
import PropTypes from 'prop-types'
import EventView from './EventView'
import {format, isSameDay} from 'date-fns'

const EventColumn = ({daysEsr, date, selectedEvents, onEventClick, onHeaderClick}) => {
  var header = format(date, 'ddd D');
  var todayStyle = {};
  if (isSameDay(date, new Date())) {
    todayStyle = {
      backgroundColor: "#dff0d8",
      border: "solid thin #ccc",
      top: "-23px"
    };
  }
  var daysEvents = [];
  for (var i = 0; i < daysEsr.length; i++) {
    daysEvents.push(daysEsr[i].event);
  }
  return (
    <div className="cal-day">
      <div className="cal-day__title" style={todayStyle} onClick={() => onHeaderClick(daysEvents)}>
        {header}
      </div>
      {daysEsr.map((esr, i) => {
        if (esr) {
          let selected = selectedEvents.filter(e => esr.event.id == e.id && e.start_datetime == esr.event.start_datetime)
          return <EventView
                    key={i}
                    {...esr}
                    onClick={() => onEventClick(esr.event)}
                    selected={selected.length > 0}
                  />
        }
      })}
    </div>
  )
}

EventColumn.propTypes = {
  daysEsr: PropTypes.arrayOf(PropTypes.shape({
    event: PropTypes.object.isRequired,
    // roll: PropTypes.object.isRequired,
    // slip: PropTypes.object.isRequired,
  }).isRequired).isRequired,
  selectedEvents: PropTypes.arrayOf(PropTypes.object.isRequired).isRequired,
  onEventClick: PropTypes.func.isRequired
}

export default EventColumn
