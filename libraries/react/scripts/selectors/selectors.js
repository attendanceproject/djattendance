//reducers change state (see reducers.js)
//selectors take state and make it usable by components (selectors turn state into props)
//reselect is a library that memoizes selectors so that it is memory efficient to do so
import { createSelector } from 'reselect'
import { startOfWeek, endOfWeek, differenceInWeeks, addDays, getDay }from 'date-fns'

//set manipulations used to do array computations quickly & easily from https://www.npmjs.com/package/set-manipulator
import { union, intersection, difference, complement, equals } from 'set-manipulator';

import { lastLeaveslip, compareEvents, categorizeEventStatus, getPeriodFromDate } from '../constants'

//defining base states
const form = (state) => state.form
const date = (state) => state.date
const selectedEvents = (state) => state.selectedEvents
const show = (state) => state.show
const rolls = (state) => state.rolls
const leaveslips = (state) => state.leaveslips
const groupslips = (state) => state.groupslips
const events = (state) => state.events
const groupevents = (state) => state.groupevents
const trainee = (state) => state.trainee
const trainees = (state) => state.trainees
const tas = (state) => state.tas
const term = (state) => state.term
const key = (state) => state.key

export const lastLeaveslips = createSelector(
  [leaveslips],
  (leaveslips) => {
    return [
      lastLeaveslip(leaveslips, 'MEAL', 'A'),
      lastLeaveslip(leaveslips, 'NIGHT', 'A'),
    ].filter((l) => l)
  }
)

export const getDateDetails = createSelector(
  [date, term],
  (date, term) => {
    let startDate = startOfWeek(date, {weekStartsOn: 1})
    let endDate = endOfWeek(date, {weekStartsOn: 1})
    let period = getPeriodFromDate(term, date)

    let difference = differenceInWeeks(startDate, new Date(term.start));
    if (difference % 2 == 1) {
      var secondStart = startDate,
        secondEnd = endDate,
        firstStart = addDays(startDate, -7),
        firstEnd = addDays(endDate, -7),
        isFirst = false
    } else {
      var firstStart = startDate,
        firstEnd = endDate,
        secondStart = addDays(startDate, 7),
        secondEnd = addDays(endDate, 7),
        isFirst = true
    }

    return {
      currentPeriod: getPeriodFromDate(term, new Date()) + 1,
      weekStart: isFirst ? firstStart : secondStart,
      weekEnd: isFirst ? firstEnd : secondEnd,
      isFirst: isFirst,
      firstStart: firstStart,
      firstEnd: firstEnd,
      secondStart: secondStart,
      secondEnd: secondEnd,
      period: period
    }
  }
)

export const getEventsforPeriod = createSelector(
  [getDateDetails, events, groupevents, show],
  (dates, events, groupevents, show) => {
    //check to display group events for group leave slips.
    if (show === 'groupslip') {
      events = groupevents
    }
    let t = events.filter((o) => {
      //deal with timezone hours offset when creating date.
      let start = new Date(o.start_datetime)
      let end = new Date(o.end_datetime)
      return (dates.firstStart < start && dates.secondEnd > end)
    });
    return t;
  }
)

export const getESRforWeek = createSelector(
  [getEventsforPeriod, leaveslips, groupslips, rolls, trainee],
  (week_events, leaveslips, groupslips, rolls, trainee) => {
    let esr = [];
    week_events.forEach((event) => {
      let a = {};
      a.event = {...event};
      leaveslips.forEach((slip) => {
        slip.events.some((ev) => {
          if(ev.id == event.id && ev.date == event.start_datetime.split("T")[0]) {
            a.event.slip = {...slip}
            return true;
          }
        return false;
        })
      });
      //if groupslip falls into range of event
      groupslips.some((gsl) => {
        if ((gsl.start < event.end_datetime && gsl.end > event.start_datetime) ||
            (event.start_datetime == event.end_datetime && gsl.start <= event.end_datetime && gsl.end >= event.start_datetime)) {
          a.event.gslip = {...gsl};
          return true;
        }
        return false;
      })
      rolls.some((roll) => {
        if (roll.event == event.id && roll.date == event.start_datetime.split("T")[0]) {
          a.event.roll = {...roll}
          return true;
        }
        return false;
      })
      esr.push(a);
    })
    return esr;
  }
)

// get events with roll/ls data, sorted by absenses, tardies, pending & excused
// use constants.js -> categorizeEventStatus to describe the event
export const getEventsByRollStatus = createSelector(
  [getESRforWeek],
  (esrs) => {
    let evs = esrs.map(esr => {
      esr.event.status = categorizeEventStatus(esr.event)
      return esr
    })
    return evs;
  }
)

export const getEventsByCol = createSelector(
  [getESRforWeek, date],
  (events, date) => {
    let weekStart = startOfWeek(date, {weekStartsOn: 1})
    let cols = []
    for (let i = 0; i < 7; i++) {
      let dayESR = events.filter(esr => {
        let day = getDay(esr.event.start_datetime) - 1
        return (day < 0 ? day+7 : day) === i && startOfWeek(esr.event.start_datetime, {weekStartsOn: 1}).getTime() === weekStart.getTime();
      }).map(esr => {
        return {
          ...esr,
          status: categorizeEventStatus(esr.event)
        }
      }).sort(compareEvents)

      // have to do some funky business because dateFns.getDay returns LD as first but we want LD to be last
      cols.push(
        {
          date: addDays(weekStart, i),
          daysEsr: dayESR,
        }
      )
    }
    return cols;
  }
)

export const getLeaveSlipsforPeriod = createSelector(
  [leaveslips, getDateDetails],
  (ls, dates) => {
    return ls.filter(slip => {
        return slip.events.some(ev =>
            dates.firstStart <= new Date(ev.date) &&
            dates.secondEnd >= new Date(ev.date))
    })
  }
)

export const getGroupSlipsforPeriod = createSelector(
  [groupslips, getDateDetails],
  (ls, dates) =>
  {
    return ls.filter(slip =>
      dates.firstStart < new Date(slip.start) && dates.secondEnd > new Date(slip.end)
    )
  }
)
