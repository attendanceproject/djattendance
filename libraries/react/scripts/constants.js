import { addDays, differenceInWeeks, startOfWeek } from 'date-fns'

//constants

export const ATTENDANCE_MONITOR_GROUP = 4

export const ATTENDANCE_STATUS = [
  {id: 'P', name: 'Present'},
  {id: 'A', name: 'Absent'},
  {id: 'T', name: 'Tardy'},
  {id: 'U', name: 'Uniform'},
  {id: 'L', name: 'Left Class'},
]

export const ATTENDANCE_STATUS_LOOKUP = {
    'P': 'present',
    'A': 'absent',
    'T': 'tardy',
    'U': 'uniform',
    'L': 'left-class'
}

export const SLIP_STATUS_LOOKUP = {
    'A': 'approved',
    'P': 'pending',
    'F': 'fellowship',
    'D': 'denied',
    'S': 'approved' //by TA sister
}

export const GROUP_SLIP_TYPES = [
  {id: 'CONF', name: 'Conference'},
  {id: 'FWSHP', name: 'Fellowship'},
  {id: 'GOSP', name: 'Gospel'},
  {id: 'OTHER', name: 'Other'},
  {id: 'SERV', name: 'Service'},
  {id: 'TTRIP', name: 'Team Trip'},
  {id: 'NOTIF', name: 'Notification Only'},
]

export const SLIP_TYPES = [
  {id: 'CONF', name: 'Conference'},
  {id: 'FWSHP', name: 'Fellowship'},
  {id: 'GOSP', name: 'Gospel'},
  {id: 'MEAL', name: 'Meal Out'},
  {id: 'NIGHT', name: 'Night Out'},
  {id: 'OTHER', name: 'Other'},
  {id: 'SERV', name: 'Service'},
  {id: 'SICK', name: 'Sickness'},
  {id: 'EMERG', name: 'Special: Family Emergency'},
  {id: 'FUNRL', name: 'Special: Funeral'},
  {id: 'INTVW', name: 'Special: Graduate School or Job Interview'},
  {id: 'GRAD', name: 'Special: Graduation'},
  {id: 'WED', name: 'Special: Wedding'},
  {id: 'NOTIF', name: 'Notification Only'},
]

export const TA_IS_INFORMED = {id: 'true', name: 'Yes, by a TA'}
export const TA_EMPTY = {id: '-1', name: ''}

export const INFORMED = [
  TA_IS_INFORMED,
  {id: 'texted', name: 'Yes, by the attendance number (only for sisters if the office is closed)'},
  {id: 'false', name: 'No'},
  TA_EMPTY,
]

export const SLIP_TYPE_LOOKUP = {
    'CONF': 'Conference',
    'EMERG': 'Family Emergency',
    'FWSHP': 'Fellowship',
    'FUNRL': 'Funeral',
    'GOSP': 'Gospel',
    'INTVW': 'Grad School/Job Interview',
    'GRAD': 'Graduation',
    'MEAL': 'Meal Out',
    'NIGHT': 'Night Out',
    'OTHER': 'Other',
    'SERV': 'Service',
    'SICK': 'Sickness',
    'SPECL': 'Special',
    'WED': 'Wedding',
    'NOTIF': 'Notification Only'
}

export const FA_ICON_LOOKUP = {
    "pending": "circle-thin",
    "denied": "minus-circle",
    "approved": "check-circle",
    "fellowship": "exclamation-circle"
}

export function joinValidClasses(classes) {
  return classes.filter((c) => c).join(' ');
};

export function categorizeEventStatus(wesr) {
  let status = {}

  let slip = wesr.slip || {}
  let gslip = wesr.gslip || {}
  let statuses = [slip.status, gslip.status]
  if (statuses.includes('A')) {
    status.slip = 'approved'
  } else if (statuses.includes('F')) {
    status.slip = 'fellowship'
  } else if (statuses.includes('P') || statuses.includes('S')) {
    status.slip = 'pending'
  } else if (statuses.includes('D')) {
    status.slip = 'denied'
  }

  if (!wesr.roll) {
    status.roll = 'present'
  } else if(wesr.roll.status === "A") {
    status.roll = 'absent'
  } else if(['T', 'U', 'L'].includes(wesr.roll.status)) {
    status.roll = 'tardy'
  }

  return status
}

export function canSubmitRoll(dateDetails) {
  let weekStart = dateDetails.weekStart
  let weekEnd = addDays(dateDetails.weekEnd, 2)
  let rollDate = new Date()
  return (rollDate >= weekStart && rollDate <= weekEnd)
}

export function canFinalizeRolls(rolls, dateDetails) {
  let weekStart = dateDetails.weekStart
  let weekEnd = dateDetails.weekEnd
  let isWeekFinalized = rolls.filter(function(roll) {
    let rollDate = new Date(roll.date)
    return rollDate >= weekStart && rollDate <= weekEnd && roll.finalized
  }).length > 0
  let now = new Date()
  // Monday midnight is when you can begin finalizing
  let isPastMondayMidnight = now >= weekEnd
  // Tuesday midnight is when you can no longer finalize
  weekEnd = addDays(weekEnd, 2)
  let isBeforeTuesdayMidnight = now <= weekEnd
  let canFinalizeWeek = !isWeekFinalized && isPastMondayMidnight && isBeforeTuesdayMidnight
  return canFinalizeWeek
}

export const compareLeaveslipEvents = (e1, e2) => {
  return new Date(e1.date) < new Date(e2.date) ? -1 : 1
}

export const compareEvents = (e1, e2) => {
  return new Date(e1.start_datetime) < new Date(e2.start_datetime) ? -1 : 1
}

export const compareLeaveslips = (ls1, ls2) => {
  let ls1Date = new Date(ls1.events.sort(compareLeaveslipEvents).slice(-1)[0].date)
  let ls2Date = new Date(ls2.events.sort(compareLeaveslipEvents).slice(-1)[0].date)
  return ls1Date < ls2Date ? -1 : 1
}

export function lastLeaveslip(leaveslips, type, status) {
  let matchingSlips = leaveslips.filter((ls) => {
    return ls.status == status && ls.type == type
  })
  return matchingSlips.sort(compareLeaveslips).slice(-1)[0]
}

export function getPeriodFromDate(term, date) {
  let period = Math.floor(
    differenceInWeeks(
      startOfWeek(date, {weekStartsOn: 1}),
      new Date(term.start)
    ) / 2
  )
  // if it's interim
  if (period < 0) {
    return 0
  }
  return period
}

export const taInformedToServerFormat = ta_informed => {
  if (ta_informed.id == "texted") {
    return {
      texted: true,
      informed: false,
    }
  } else if (ta_informed.id != "true") {
    return {
      texted: false,
      informed: false,
    }
  } else {
    return {
      informed: true,
      texted: false,
    }
  }
}
