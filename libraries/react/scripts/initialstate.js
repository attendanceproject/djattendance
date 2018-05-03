var trainee = require("./testdata/trainee");
var trainees = require("./testdata/trainees");
var tas = require("./testdata/tas");
var events = require("./testdata/events-small");
var rolls = require("./testdata/rolls");
var iSlips = require("./testdata/individualSlips");
var gSlips = require("./testdata/groupSlips");
var term = require("./testdata/term");
var groupevents = require("./testdata/groupevents");
var date = new Date();
var selectedEvents = [];
var show = 'summary';

import { TA_IS_INFORMED, TA_EMPTY } from './constants'

//see attendance_react.html
if (typeof Trainee !== 'undefined') {
  if (Trainee.constructor === Array) {
    trainee = Trainee[0];
  } else {
    trainee = Trainee;
  }
}
if (typeof Term !== 'undefined') {
  if (Term.constructor === Array) {
    term = Term[0];
  } else {
    term = Term;
  }
}
if (typeof Trainees !== 'undefined') {
  trainees = Trainees;
}
if (typeof TAs !== 'undefined') {
  tas = TAs;
}
if (typeof Events !== 'undefined') {
  events = Events;
}
if (typeof GroupEvents !== 'undefined') {
  groupevents = GroupEvents;
}
if (typeof Rolls !== 'undefined') {
  rolls = Rolls;
}
if (typeof IndividualSlips !== 'undefined') {
  iSlips = IndividualSlips;
}
if (typeof GroupSlips !== 'undefined') {
  gSlips = GroupSlips;
}
if (typeof Today !== 'undefined') {
  date = Today;
}
if (typeof SelectedEvents !== 'undefined') {
  selectedEvents = SelectedEvents;
}
if (typeof Show != 'undefined') {
  show = Show;
}

var initialState = {
  show: show,
  form: {
    rollStatus: {},
    leaveSlip: {
      description: "",
      slipType: {},
      ta_informed: TA_EMPTY,
      ta: TA_EMPTY,
      id: null,
    },
    groupSlip: {
      description: "",
      slipType: {},
      ta_informed: TA_EMPTY,
      ta: TA_EMPTY,
      trainees: [],
      id: null,
    },
    traineeView: trainee,
  },
  selectedEvents: selectedEvents,
  date: date,
  rolls: rolls,
  leaveslips: iSlips,
  groupslips: gSlips,
  groupevents: groupevents,
  events: events,
  trainee: User || trainee,
  trainees: trainees,
  tas: tas,
  term: term,
  showLegend: true,

  submitting: false,
  formSuccess: null,
};

export default initialState;
