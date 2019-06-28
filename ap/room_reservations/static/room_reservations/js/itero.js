/***************************
 * CONFIRUGATION VARIABLES *
 ***************************/
var NUM_ROWS = 5;

var TIMELIST = ["5:30", "6:00", "6:15", "6:30", "7:00", "7:30", "8:00",
  "8:30", "9:00", "9:30", "9:45", "10:00", "10:15", "10:45", "11:00", "11:15", "11:45",
  "12:00", "12:30", "12:45", "13:00", "13:30", "13:50", "14:15", "14:00", "14:30", "15:00", 
  "15:30", "15:50", "16:00", "16:15", "16:45", "16:55", "17:00", "17:30", "17:55", "18:00",
  "18:15", "18:30", "19:00", "19:45", "20:00", "20:30", "21:00", "21:30", "22:00",
  "22:30", "23:00"];

var ROW_STYLES = {
  "6:30": "background-color: lightgrey; color: black",
  "10:15": "background-color: yellow; color: black",
  "12:30": "background-color: yellow; color: black",
  "13:30": "background-color: #66a3ff; color: black",
  "16:10": "background-color: yellow; color: black",
  "18:00": "background-color: yellow; color: black",
  "19:00": "background-color: #66a3ff; color: black"
};

var SERVICE_GROUPS = {
  /*** Thursday ***/
  "4/4/2019": [
    {
      "name": "Events and Tasks",
      "color": "White",
      "res": [
        { "time": "8:25-11:30", "content": "Unload,Inventory,Organize Truck" },
        { "time": "11:45-12:30", "content": "Arrive, POW WOW and eat" },
        { "time": "12:30-13:30", "content": "Organize CAF/Setup SL" },
        { "time": "13:30-14:00", "content": "Trainees arrive" },
        { "time": "14:00-17:15", "content": "SL Assembly/TB Setup" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "Trainees leave" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Trainee roll in" },
        { "time": "19:30-20:30", "content": "SL Assembly/Finish Tables" },
        { "time": "20:30-21:00", "content": "Trainees leave" },
        { "time": "21:00-22:00", "content": "Finish all tasks for assembly" },
        { "time": "22:00-22:30", "content": "Enjoy the Lord and depart" }
      ]
    },

    {
      "name": "Admin",
      "color": "lightPink",
      "res": [
        { "time": "8:25-11:30", "content": "Arrange CAF" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Arrange CAF, Prep roll call" },
        { "time": "13:30-14:00", "content": "Roll In Trainees" },
        { "time": "14:00-17:15", "content": "Oversee, Setup Breakfast Items" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:30", "content": "Roll Out Trainees" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-20:30", "content": "Oversee" },
        { "time": "20:30-21:00", "content": "Roll Out Trainees" },
        { "time": "21:00-22:00", "content": "Oversee, Coordinate Rides" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Aux",
      "color": "#ffe4b2",
      "res": [
        { "time": "8:25-11:30", "content": "UIO" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Lead Unloading, Check invoices" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Organize Truck, INV, Help INV" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:30", "content": "KC Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-20:30", "content": "Secure Carts for TEA BAR" },
        { "time": "20:30-22:00", "content": "Help TEA BAR" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Dinner",
      "color": "lightyellow",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Prep, Fill Sauce Cups" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "DINNER prep" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:30", "content": "KC Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:0-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-22:00", "content": "DINNER prep" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Dishes",
      "color": "lightgreen",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Fill Sauce cups/Help AUX" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Help TEA BAR" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-20:30", "content": "Help TEA BAR, SL" },
        { "time": "20:30-22:00", "content": "Help TEA BAR" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Drivers",
      "color": "lightblue",
      "res": [
        { "time": "8:25-11:30", "content": "UIO" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Help AUX" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Help INV" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-20:30", "content": "Help INV" },
        { "time": "20:30-22:00", "content": "Help TEA BAR" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Inventory",
      "color": "#EAADEA",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Check deliveries and distribute" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Prep. L&T" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-22:00", "content": "Finish L&T, finalize inventory" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Sack Lunch",
      "color": "lightpink",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Prep 2nd yr Class" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:45", "content": "SL Assembly, drop non-perishables" },
        { "time": "17:15-17:15", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-22:00", "content": "Continue SL assembly" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Setup",
      "color": "#ffe4b2",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Intentory Items, Prep" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:45", "content": "Table prep" },
        { "time": "17:15-17:15", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-22:00", "content": "Table Prep" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Tea Bar",
      "color": "lightyellow",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Finish stations, help INV" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Fill urns, bins, distribute water" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-20:30", "content": "Set up carts, stations" },
        { "time": "20:30-22:00", "content": "Finish, leave ASAP" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Trash",
      "color": "lightGreen",
      "res": [
        { "time": "8:25-11:30", "content": "UIO" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Help AUX" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Trash can set-up" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-21:30", "content": "Finish trash and recycle bins" },
        { "time": "21:30-20:30", "content": "Finish trash and recycle bins" },
        { "time": "20:30-21:00", "content": "Help TEA BAR" },
        { "time": "21:00-22:00", "content": "Help TEA BAR" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Special",
      "color": "lightblue",
      "res": [
        { "time": "8:25-11:30", "content": "Class" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Help INV" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Set up snack bar" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-21:30", "content": "Help SETUP" },
        { "time": "21:30-20:30", "content": "Help SETUP" },
        { "time": "20:30-21:00", "content": "Help SL" },
        { "time": "21:00-22:00", "content": "Help SL" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    },

    {
      "name": "Cook",
      "color": "#EAADEA",
      "res": [
        { "time": "8:25-11:30", "content": "Brothers: UIO" },
        { "time": "11:45-12:30", "content": "POW WOW/Lunch" },
        { "time": "12:30-13:30", "content": "Help AUX" },
        { "time": "13:30-14:00", "content": "Orientation" },
        { "time": "14:00-17:15", "content": "Prep Breakfast Items" },
        { "time": "17:15-17:45", "content": "Clean-up and Setup FTTA Dinner"},
        { "time": "17:45-18:40", "content": "KC Dinner" },
        { "time": "18:40-19:00", "content": "POW WOW" },
        { "time": "19:00-19:30", "content": "Roll in Trainees" },
        { "time": "19:30-21:30", "content": "Pack dinner, arrange assembly" },
        { "time": "21:30-20:30", "content": "Pack dinner, arrange assembly" },
        { "time": "20:30-21:00", "content": "Talk with sister Ann" },
        { "time": "21:00-22:00", "content": "Talk with sister Ann" },
        { "time": "22:00-22:30", "content": "POW WOW" }
      ]
    }
  ],
  /*** Friday ***/
  "4/5/2019": [
    {
      "name": "ITERO",
      "color": "lightblue",
      "res": [
        { "time": "7:30-8:30", "content": "Registration " },
        { "time": "8:30-10:15", "content": "SESSION 1" },
        { "time": "10:15-10:45", "content": "BREAK" },
        { "time": "10:45-12:30", "content": "SESSION 2" },
        { "time": "12:30-13:00", "content": "LUNCH" },
        { "time": "13:00-15:45", "content": "BREAK" },
        { "time": "15:45-16:00", "content": "TRAVEL" },
        { "time": "16:00-18:00", "content": "STUDY" },
        { "time": "18:00-19:00", "content": "DINNER" },
        { "time": "19:00-21:00", "content": "MEETING" }
      ]
    },

    {
      "name": "Events and Tasks",
      "color": "White",
      "res": [
        { "time": "5:30-6:15", "content": "TEA BAR Arrives" },
        { "time": "6:15-6:30", "content": "Arrive and enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast/Make Sandwiches" },
        { "time": "7:30-9:00", "content": "Prepare for MA trainee arrival" },
        { "time": "9:00-9:30", "content": "MA Trainees arrive" },
        { "time": "9:30-10:00", "content": "Sack lunch assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "FTTA Lunch assembly" },
        { "time": "10:30-10:45", "content": "Load FTTA lunches onto VAN" },
        { "time": "10:45-11:00", "content": "Service groups grab sack lunches" },
        { "time": "11:00-11:15", "content": "Deliver SL to old TC" },
        { "time": "11:15-11:45", "content": "Coordinate with REG for lunch ushering" },
        { "time": "11:45-12:00", "content": "Usher orientation in bookstore" },
        { "time": "12:00-12:30", "content": "KC teams move to floor" },
        { "time": "12:30-12:45", "content": "ITERO Lunch + MA Trainees leave" },
        { "time": "12:45-13:00", "content": "Count Leftovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-13:50", "content": "Trainees Arrive" },
        { "time": "13:50-14:15", "content": "Dinner/Captain Orientation" },
        { "time": "14:15-15:30", "content": "SL assembly and restock tea bars" },
        { "time": "15:30-16:15", "content": "Dinner Prep" },
        { "time": "16:15-16:45", "content": "Trainee Break" },
        { "time": "16:45-16:55", "content": "Trainees Come Back from Break" },
        { "time": "16:55-17:00", "content": "COOKING puts out food, dinner assembly Runthrough" },
        { "time": "17:00-17:30", "content": "Dinner assembly" },
        { "time": "17:30-17:55", "content": "Driver Transports to REG" },
        { "time": "17:55-18:00", "content": "Ready for Dinner Distribution" },
        { "time": "18:00-18:15", "content": "Dinner service begins" },
        { "time": "18:15-18:30", "content": "Begin dinner cleanup" },
        { "time": "18:30-19:00", "content": "KC Dinner POW WOW" },
        { "time": "19:00-19:45", "content": "Trainees Roll in" },
        { "time": "19:45-21:30", "content": "Cleanup, prepare for next day" },
        { "time": "21:30-22:00", "content": "Trainees leave + POW WOW" },
        { "time": "22:00-22:30", "content": "Leave" }
      ]
    },

    {
      "name": "Admin",
      "color": "lightPink",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Arrive and Enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Oversee/Prepare for MA" },
        { "time": "9:00-9:30", "content": "Roll in MA Trainees" },
        { "time": "9:30-10:00", "content": "Oversee/Trainee Distribution" },
        { "time": "10:00-10:15", "content": "Prepare for Bag DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:00", "content": "Oversee" },
        { "time": "12:00-12:30", "content": "Roll out MA Trainees" },
        { "time": "12:30-13:00", "content": "Setup CAF/Prep for FTTA" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW + Lefovers" },
        { "time": "13:30-13:50", "content": "Roll In FTTA Trainees" },
        { "time": "13:50-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Oversee" },
        { "time": "15:30-16:45", "content": "Check with Teams/Prep FTTA" },
        { "time": "16:45-16:55", "content": "Roll in FTTA" },
        { "time": "16:55-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help Cleanup/Trainee Dist" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-19:45", "content": "Roll in Trainees" },
        { "time": "19:45-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "Roll Out Trainees" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Aux",
      "color": "#ffe4b2",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Arrive and Enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Help SL" },
        { "time": "10:00-10:15", "content": "Grab Perishables" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Counter Leftovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch/POW WOW" },
        { "time": "13:30-13:50", "content": "Help SL" },
        { "time": "13:50-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Help SL" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:50", "content": "Help Cooking" },
        { "time": "16:50-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dinner",
      "color": "lightyellow",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-10:15", "content": "DINNER prep" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch/POW WOW" },
        { "time": "13:30-13:50", "content": "KC Intro" },
        { "time": "13:50-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Captain Orientation" },
        { "time": "15:30-16:50", "content": "Dinner Prep" },
        { "time": "16:45-18:30", "content": "Lead Dinner Service" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dishes",
      "color": "lightgreen",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-9:00", "content": "Fill Sauce Cups/Wash Dishes" },
        { "time": "9:00-10:15", "content": "Fill Sauce Cups/Help SL" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Fill Sauce Cups" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:45", "content": "Help Cooking" },
        { "time": "16:45-17:55", "content": "Wash Dishes" },
        { "time": "17:45-18:00", "content": "Dispense food to service groups" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-19:30", "content": "Recieve Trainees" },
        { "time": "19:30-21:30", "content": "Wash" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Drivers",
      "color": "lightblue",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Help SL" },
        { "time": "10:00-10:15", "content": "Prepare Van" },
        { "time": "10:15-10:30", "content": "Bag Drop" },
        { "time": "10:30-10:45", "content": "Load SL" },
        { "time": "10:45-12:00", "content": "Deliver SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Help SL" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:45", "content": "Help Cooking" },
        { "time": "16:45-17:30", "content": "Help DINNER" },
        { "time": "17:30-18:00", "content": "Transport to REG" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Bring back leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup SL" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Inventory",
      "color": "#EAADEA",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Prepare L&T" },
        { "time": "9:00-9:45", "content": "L&T/Salads" },
        { "time": "9:45-10:00", "content": "Load Salads onto Truck" },
        { "time": "10:00-10:15", "content": "L&T/Inventory" },
        { "time": "10:15-12:00", "content": "Help SL" },
        { "time": "12:00-13:00", "content": "Salads/Cleanup" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Salad prep" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Count Leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Lettuce & Tomatoe" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Sack Lunch",
      "color": "lightpink",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Prepare for SL assembly" },
        { "time": "9:00-10:00", "content": "SL assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-10:45", "content": "FTTA Sack Lunch" },
        { "time": "10:45-12:00", "content": "Arrange Floor" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "SL assembly" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "SL Assembly" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Setup",
      "color": "#ffe4b2",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-9:00", "content": "Finalize set up" },
        { "time": "9:00-10:00", "content": "bags, baskets, utensils" },
        { "time": "10:00-10:15", "content": "Load Butter into Truck" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Setup tables" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Lead Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Tea Bar",
      "color": "lightyellow",
      "res": [
        { "time": "5:30-6:15", "content": "Arrive, Turn on Urns" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "On floor 7:20 for REG" },
        { "time": "8:30-9:00", "content": "Restock" },
        { "time": "9:00-10:00", "content": "Restock carts" },
        { "time": "10:00-10:15", "content": "Monitor Stations" },
        { "time": "10:15-12:00", "content": "Setup Station 1, Restock Carts" },
        { "time": "12:00-13:00", "content": "Monitor Stations" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Restock carts" },
        { "time": "15:30-16:45", "content": "Restock, sanitize and inventory" },
        { "time": "16:45-18:00", "content": "Restock, sanitize and inventory" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Restock" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Trash",
      "color": "lightGreen",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Trash Run" },
        { "time": "9:00-10:00", "content": "Help SL" },
        { "time": "10:00-10:45", "content": "Trash Run" },
        { "time": "10:45-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Receive Trainees" },
        { "time": "14:15-16:45", "content": "Trash Run" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Lead Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Special",
      "color": "lightblue",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Help SL" },
        { "time": "9:00-10:00", "content": "Prepare Snack bar" },
        { "time": "10:00-10:15", "content": "Bag drop" },
        { "time": "10:15-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-15:30", "content": "Help SL" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help Dinner/Take care of Co-workers dinners" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Cook",
      "color": "#EAADEA",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Cook" },
        { "time": "9:00-12:00", "content": "Cook/Help SL" },
        { "time": "12:00-13:00", "content": "Dinner Appointment" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Dinner Orientation" },
        { "time": "14:15-16:45", "content": "Cook" },
        { "time": "16:45-18:00", "content": "Put out Food and Restock" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Count Leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Prep" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    }
  ],
  /*** Saturday ***/
  "4/6/2019": [
    {
      "name": "ITERO",
      "color": "lightblue",
      "res": [
        { "time": "8:30-10:15", "content": "SESSION 1" },
        { "time": "10:15-10:45", "content": "BREAK" },
        { "time": "10:45-12:30", "content": "SESSION 2" },
        { "time": "12:30-13:00", "content": "LUNCH" },
        { "time": "13:00-15:45", "content": "BREAK" },
        { "time": "15:45-16:00", "content": "TRAVEL" },
        { "time": "16:00-18:00", "content": "STUDY" },
        { "time": "18:00-19:00", "content": "DINNER" },
        { "time": "19:00-21:00", "content": "MEETING" }
      ]
    },

    {
      "name": "Events and Tasks",
      "color": "White",
      "res": [
        { "time": "5:30-6:15", "content": "TEA BAR Arrives" },
        { "time": "6:15-6:30", "content": "Arrive and enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast/Make Sandwiches" },
        { "time": "7:30-9:00", "content": "Prepare for MA trainee arrival" },
        { "time": "9:00-9:30", "content": "MA Trainees arrive" },
        { "time": "9:30-10:00", "content": "Sack lunch assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "FTTA Lunch assembly" },
        { "time": "10:30-10:45", "content": "Load FTTA lunches onto VAN" },
        { "time": "10:45-11:00", "content": "Service groups grab sack lunches" },
        { "time": "11:00-11:15", "content": "Deliver SL to old TC" },
        { "time": "11:15-11:45", "content": "Coordinate with REG for lunch ushering" },
        { "time": "11:45-12:00", "content": "Usher orientation in bookstore" },
        { "time": "12:00-12:30", "content": "KC teams move to floor" },
        { "time": "12:30-12:45", "content": "ITERO Lunch + MA Trainees leave" },
        { "time": "12:45-13:00", "content": "Count Leftovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-13:50", "content": "Trainees Arrive" },
        { "time": "13:50-14:15", "content": "Sack Lunch Assembly" },
        { "time": "14:15-15:30", "content": "Restock and Sanitizetea bars" },
        { "time": "15:30-16:15", "content": "Dinner Prep" },
        { "time": "16:15-16:45", "content": "Trainee Break" },
        { "time": "16:45-16:55", "content": "Trainees Come Back from Break" },
        { "time": "16:55-17:00", "content": "COOKING puts out food, dinner assembly Runthrough" },
        { "time": "17:00-17:30", "content": "Dinner assembly" },
        { "time": "17:30-17:55", "content": "Driver Transports to REG" },
        { "time": "17:55-18:00", "content": "Ready for Dinner Distribution" },
        { "time": "18:00-18:15", "content": "Dinner service begins" },
        { "time": "18:15-18:30", "content": "Begin dinner cleanup" },
        { "time": "18:30-19:00", "content": "KC Dinner POW WOW" },
        { "time": "19:00-19:45", "content": "Trainees Roll in" },
        { "time": "19:45-21:30", "content": "Cleanup, prepare for next day" },
        { "time": "21:30-22:00", "content": "Trainees leave + POW WOW" },
        { "time": "22:00-22:30", "content": "Leave" }
      ]
    },

    {
      "name": "Admin",
      "color": "lightPink",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Arrive and Enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Oversee/Prepare for MA" },
        { "time": "9:00-9:30", "content": "Roll in MA Trainees" },
        { "time": "9:30-10:00", "content": "Oversee/Trainee Distribution" },
        { "time": "10:00-10:15", "content": "Prepare for Bag DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:00", "content": "Oversee" },
        { "time": "12:00-12:30", "content": "Roll out MA Trainees" },
        { "time": "12:30-13:00", "content": "Setup CAF/Prep for FTTA" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW + Lefovers" },
        { "time": "13:30-13:50", "content": "Roll In FTTA Trainees" },
        { "time": "13:50-14:15", "content": "Oversee" },
        { "time": "14:15-15:30", "content": "Check with Teams" },
        { "time": "15:30-16:45", "content": "Prepare for Trainee Help" },
        { "time": "16:45-16:55", "content": "Roll in FTTA" },
        { "time": "16:55-18:00", "content": "Oversee, Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help Cleanup/Trainee Dist" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-19:45", "content": "Roll in Trainees" },
        { "time": "19:45-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "Roll Out Trainees" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Aux",
      "color": "#ffe4b2",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Arrive and Enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Help SL" },
        { "time": "10:00-10:15", "content": "Grab Perishables" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Counter Leftovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch/POW WOW" },
        { "time": "13:30-15:30", "content": "Help SL" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:50", "content": "Help Cooking" },
        { "time": "16:50-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dinner",
      "color": "lightyellow",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-10:15", "content": "DINNER prep" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch/POW WOW" },
        { "time": "13:30-16:50", "content": "Dinner Prep" },
        { "time": "16:45-18:30", "content": "Lead Dinner Service" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dishes",
      "color": "lightgreen",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-9:00", "content": "Fill Sauce Cups/Wash Dishes" },
        { "time": "9:00-10:15", "content": "Fill Sauce Cups/Help SL" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Fill Sauce Cups" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:45", "content": "Help Cooking" },
        { "time": "16:45-17:55", "content": "Wash Dishes" },
        { "time": "17:45-18:00", "content": "Dispense food to service groups" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-19:30", "content": "Recieve Trainees" },
        { "time": "19:30-21:30", "content": "Wash" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Drivers",
      "color": "lightblue",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Help SL" },
        { "time": "10:00-10:15", "content": "Prepare Van" },
        { "time": "10:15-10:30", "content": "Bag Drop" },
        { "time": "10:30-10:45", "content": "Load SL" },
        { "time": "10:45-12:00", "content": "Deliver SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Help SL" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-16:45", "content": "Help Cooking" },
        { "time": "16:45-17:30", "content": "Help DINNER" },
        { "time": "17:30-18:00", "content": "Transport to REG" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Bring back leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup SL" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Inventory",
      "color": "#EAADEA",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Prepare L&T" },
        { "time": "9:00-9:45", "content": "L&T/Salads" },
        { "time": "9:45-10:00", "content": "Load Salads onto Truck" },
        { "time": "10:00-10:15", "content": "L&T/Inventory" },
        { "time": "10:15-12:00", "content": "Help SL" },
        { "time": "12:00-13:00", "content": "Salads/Cleanup" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Salad prep" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Count Leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Lettuce & Tomatoe" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Sack Lunch",
      "color": "lightpink",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Prepare for SL assembly" },
        { "time": "9:00-10:00", "content": "SL assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-10:45", "content": "FTTA Sack Lunch" },
        { "time": "10:45-12:00", "content": "Arrange Floor" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "SL assembly" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "SL Assembly" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Setup",
      "color": "#ffe4b2",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-9:00", "content": "Finalize set up" },
        { "time": "9:00-10:00", "content": "bags, baskets, utensils (setup for DINNER)" },
        { "time": "10:00-10:15", "content": "Load Butter into Truck" },
        { "time": "10:15-10:30", "content": "Help TB" },
        { "time": "10:30-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Setup tables" },
        { "time": "15:30-16:15", "content": "Break" },
        { "time": "16:15-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Lead Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Tea Bar",
      "color": "lightyellow",
      "res": [
        { "time": "5:30-6:15", "content": "Arrive, Turn on Urns" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "On floor during registration" },
        { "time": "8:30-9:00", "content": "Restock" },
        { "time": "9:00-10:00", "content": "Restock carts" },
        { "time": "10:00-10:15", "content": "Monitor Stations" },
        { "time": "10:15-12:00", "content": "Setup Station 1, Restock Carts" },
        { "time": "12:00-13:00", "content": "Monitor Stations" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Restock carts" },
        { "time": "15:30-18:00", "content": "Restock, sanitize and inventory" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Restock" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Trash",
      "color": "lightGreen",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Trash Run" },
        { "time": "9:00-10:00", "content": "Help SL" },
        { "time": "10:00-10:45", "content": "Trash Run" },
        { "time": "10:45-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Receive Trainees" },
        { "time": "14:15-16:45", "content": "Trash Run" },
        { "time": "16:45-18:00", "content": "Help DINNER" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Eat Dinner" },
        { "time": "18:30-19:00", "content": "POW WOW" },
        { "time": "19:00-21:30", "content": "Lead Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Special",
      "color": "lightblue",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Help SL" },
        { "time": "9:00-10:00", "content": "Prepare Snack bar" },
        { "time": "10:00-10:15", "content": "Bag drop" },
        { "time": "10:15-12:00", "content": "Help SL" },
        { "time": "12:00-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Leftovers" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-15:30", "content": "Help SL" },
        { "time": "15:30-16:45", "content": "Break" },
        { "time": "16:45-18:00", "content": "Help Dinner/Take care of Co-workers dinners" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Help DINNER" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Cleanup" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    },

    {
      "name": "Cook",
      "color": "#EAADEA",
      "res": [
        { "time": "5:30-6:15", "content": "" },
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-9:00", "content": "Cook" },
        { "time": "9:00-12:00", "content": "Cook/Help SL" },
        { "time": "12:00-13:00", "content": "Dinner Appointment" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-16:45", "content": "Cook" },
        { "time": "16:45-18:00", "content": "Put out Food and Restock" },
        { "time": "18:00-18:15", "content": "Dinner Service" },
        { "time": "18:15-18:30", "content": "Count Leftovers" },
        { "time": "18:30-19:00", "content": "KC Dinner, POW WOW" },
        { "time": "19:00-21:30", "content": "Prep" },
        { "time": "21:30-22:00", "content": "POWOW" },
        { "time": "22:00-22:30", "content": "Finish" }
      ]
    }
  ],
  /*** Lord's Day ***/
  "4/7/2019": [
    {
      "name": "ITERO",
      "color": "lightblue",
      "res": [
        { "time": "8:00-8:30", "content": "Lords Table " },
        { "time": "8:30-10:15", "content": "SESSION 1" },
        { "time": "10:15-10:45", "content": "BREAK" },
        { "time": "10:45-12:30", "content": "SESSION 2" },
        { "time": "12:30-13:00", "content": "LUNCH" }
      ]
    },

    {
      "name": "Events and Tasks",
      "color": "White",
      "res": [
        { "time": "6:15-6:30", "content": "Arrive and enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Sack lunch assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-11:15", "content": "BAG DROP" },
        { "time": "11:15-11:45", "content": "Coordinate with REG for lunch ushering" },
        { "time": "11:45-12:00", "content": "Usher orientation in bookstore" },
        { "time": "12:00-12:30", "content": "KC teams move to floor" },
        { "time": "12:30-12:45", "content": "ITERO Lunch" },
        { "time": "12:45-13:00", "content": "Counter Leftovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch + POW WOW" },
        { "time": "13:30-14:15", "content": "Trainees Arrive" },
        { "time": "14:15-17:00", "content": "Inventory, Clean, Organize CAF" },
        { "time": "17:00-18:00", "content": "Trainees Leave" },
        { "time": "18:00-18:30", "content": "ITERO KC Finish" }
      ]
    },

    {
      "name": "Admin",
      "color": "lightpink",
      "res": [
        { "time": "6:15-6:30", "content": "Arrive and Enjoy the Lord" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Oversee, Work on Breakdown Plan" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Oversee,Clear Truck,Move Tables" },
        { "time": "12:30-13:00", "content": "Prepare for FTTA Help" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-14:15", "content": "Roll in Trainees" },
        { "time": "14:15-17:00", "content": "Oversee" },
        { "time": "17:00-18:00", "content": "Roll Out Trainees" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Aux",
      "color": "#ffe4b2",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Help SL" },
        { "time": "10:00-10:15", "content": "Grab Perishables" },
        { "time": "10:15-10:30", "content": "Bag DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Organize Closet" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dinner",
      "color": "lightyellow",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-10:15", "content": "Help SL" },
        { "time": "10:15-10:45", "content": "Help TB" },
        { "time": "10:45-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Dishes",
      "color": "lightgreen",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-10:15", "content": "Help SL" },
        { "time": "10:15-10:45", "content": "Help TB" },
        { "time": "10:45-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Drivers",
      "color": "lightblue",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:15", "content": "Cleanup" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Inventory",
      "color": "#EAADEA",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "Prepare L&T" },
        { "time": "10:00-10:15", "content": "Help SL" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Sack Lunch",
      "color": "lightpink",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:00", "content": "SL Assembly" },
        { "time": "10:00-10:15", "content": "Prepare for BAG DROP" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-11:15", "content": "SL Assembly" },
        { "time": "11:15-12:30", "content": "Arrange Floor,Early Lunch Table" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Setup",
      "color": "#ffe4b2",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Help TB" },
        { "time": "8:30-10:15", "content": "Help SL" },
        { "time": "10:15-10:45", "content": "Help TB" },
        { "time": "10:45-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Tea Bar",
      "color": "lightyellow",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-10:00", "content": "Restock carts" },
        { "time": "10:00-10:45", "content": "Monitor Stations" },
        { "time": "10:45-13:00", "content": "Restock carts, Breakdown Stations" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Trash",
      "color": "lightgreen",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "Breakfast" },
        { "time": "7:00-8:30", "content": "Trash Run" },
        { "time": "8:30-10:00", "content": "Breakdown cardboard" },
        { "time": "10:00-10:15", "content": "Help SL" },
        { "time": "10:15-11:15", "content": "Trash Run" },
        { "time": "11:15-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Special",
      "color": "lightblue",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:15", "content": "Help SL" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Breakdown" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    },

    {
      "name": "Cook",
      "color": "#EAADEA",
      "res": [
        { "time": "6:15-6:30", "content": "Personal Morning Revival" },
        { "time": "6:30-7:00", "content": "POW WOW" },
        { "time": "7:00-7:30", "content": "Breakfast" },
        { "time": "7:30-10:15", "content": "Help SL" },
        { "time": "10:15-10:30", "content": "BAG DROP" },
        { "time": "10:30-12:30", "content": "Help SL" },
        { "time": "12:30-12:45", "content": "KC Ushers on Floor" },
        { "time": "12:45-13:00", "content": "Count Lefovers/Store Perishables" },
        { "time": "13:00-13:30", "content": "KC Lunch, POW WOW" },
        { "time": "13:30-17:00", "content": "Cleanup" },
        { "time": "17:00-18:00", "content": "POWOW" },
        { "time": "18:00-18:30", "content": "Finish" }
      ]
    }
  ]

};


/********
 * CODE *
 ********/

function loadTable() {
  var schedule = $("#schedule");
  schedule.html("");

  var times = TIMELIST.filter(function (t) {
    var cTime = currentTime();
    if(cTime.minute > 30) {
      cTime.minute = 30;
    } else {
      cTime.minute = 0;
    }
    return compareTime(parseTime(t), cTime) >= 0;
  });

  var service_groups = SERVICE_GROUPS[new Date().toLocaleString().split(",")[0]];
  if (!service_groups) {
    return;
  }
  for (var row = 0; row < NUM_ROWS + 1 && row <= times.length; row++) {
    var time = times[row - 1];
    var table_row = $("<tr></tr>", { "style": ROW_STYLES[time] });
    // offset by 1 for row and col for time and group name
    for (var col = 0; col < service_groups.length + 1; col++) {
      var service_group = service_groups[col - 1];
      var table_cell = $("<td></td>");
      if (row === 0 && col === 0) {
        table_cell.text("TIME");
      } else if (col === 0) {
        table_cell.text(printTime(parseTime(time)));
      } else if (row === 0) {
        table_cell.text(service_group.name);
      } else {
        for (var i = 0; i < service_group.res.length; i++) {
          var res = service_group.res[i];
          if (timeInTimeRange(parseTime(time), res.time)) {
            if (res.content.length >= 35) {
              var t = new Date();
              table_cell.text((t.getSeconds() % 6) > 2 ? res.content.substr(0, 35) : res.content.substr(35));
            } else {
              table_cell.text(res.content);
            }
          }
        }
      }
      table_row.append(table_cell);
    }
    schedule.append(table_row);
  }

  var cols = $("<colgroup></colgroup>");
  cols.append($("<col></col>", { "style": "background-color:white" }));
  for (var i = 0; i < service_groups.length; i++) {
    cols.append($("<col></col>", { "style": "background-color:" + service_groups[i].color }));
  }
  schedule.append(cols);

}

function printTime(time) {
  var hours = time.hour % 12;
  var hours = hours == 0 ? 12 : hours;
  var minutes = time.minute < 10 ? "0" + time.minute : time.minute;
  var ampm = time.hour >= 12 ? "PM" : "AM";
  return hours + ":" + minutes + ampm;
}

function currentTime() {
  var date = new Date();
  return parseTime(date.getHours() + ":" + date.getMinutes());
}

function parseTime(time) {
  var timeSplit = time.split(":");
  var hour = parseInt(timeSplit[0]);
  var minute = parseInt(timeSplit[1]);
  return { "hour": hour, "minute": minute };
}

function compareTime(a, b) {
  if (a.hour > b.hour) {
    return 1;
  } else if (a.hour === b.hour && a.minute > b.minute) {
    return 1;
  } else if (a.hour === b.hour && a.minute === b.minute) {
    return 0;
  }
  return -1;
}

function timeInTimeRange(t, timeRange) {
  var rangeSplit = timeRange.split("-");
  var start = parseTime(rangeSplit[0]);
  var end = parseTime(rangeSplit[1]);
  if (compareTime(t, start) >= 0 && compareTime(t, end) < 0) {
    return true;
  }
  return false;
}
var pageVersion;
var oldAns = [];
var checkAnns = false;
function displayTicker(ans) {
  $("#ticker").html("");

  //Reloads when the announcements change
  if (checkAnns) {
    if (oldAns.length !== ans.length) {
      location.reload(true);
    }
    //Check that the announcements present are the same
    var anss = ans.concat().sort();
    var oldAnss = oldAns.concat().sort();
    for (var each = 0; each < anss.length; each++) {
      if (anss[each] !== oldAnss[each]) {
        location.reload(true);
      }
    }
  }
  else {
    oldAns = ans;
    checkAnns = true;
  }
  var anslen = ans.length;
  var temp = $("<span></span>");
  //Hide the announcement section if there is no accouncement
  if (anslen < 1) {
    $("#ticker-wrap").fadeOut();
    $("#ticker-heading").fadeOut();
    $("#ticker-heading-wrap").fadeOut();
  }
  for (var i = 0; i < anslen; i++) {
    //Format ticker announcements here
    temp.append("<b></b>" + ans[i]);
    if (i + 1 !== anslen) {
      //Spacing between the announcements
      temp.append("<b>&nbsp&nbsp</b>");
    }
  }
  var anns = $("<p style=\"white-space:nowrap\"></p>");
  $("#ticker").append(anns.append(temp));
  var annsSize = $("#ticker").width();
  var headingSize = $("#ticker-heading-wrap").width();
  annsSize = $("#ticker").width() - headingSize;
  annsSize *= -1;
  //Change speed here (higher = faster)
  var speed = 12;
  if (speed <= 0) {
    speed = 10;
  }
  var screen = $(document).width();
  var totalSize = (screen - annsSize - headingSize) * 10 / speed;

  //Animates the ticker announcements if it is longer than the screen width
  if ($("#ticker").width() > screen - headingSize - 50) {
    $("#ticker").animate({ left: "100%" }, 0, "linear");
    $("#ticker").animate({ left: annsSize + "px" }, totalSize * 10, "linear");
  }
  //otherwise keep it stationary
  else {
    var buffer = headingSize + 7;
    $("#ticker").animate({ left: buffer + "px" }, 0);
  }
}

function loadTicker() {
  $.getJSON(TICKER, displayTicker)
    .fail(function () {
      displayTicker(oldAns);
    });
}

var OFFSETS = [
  { offset: 0, limit: 11, oldRooms: [] },
  { offset: 11, limit: 11, oldRooms: [] },
  { offset: 22, limit: 11, oldRooms: [] },
];

function formatAMPM(date) {
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  hours = hours ? hours : 12;
  minutes = minutes < 10 ? "0" + minutes : minutes;
  var strTime = hours + ":" + minutes + " " + ampm;
  return strTime;
}


function loadCalendar() {
  var currentOffset = OFFSETS.shift();
  $.getJSON(RESERVATIONS + "?offset=" + currentOffset.offset + "&limit=" + currentOffset.limit,
    (rooms) => {
      currentOffset.oldRooms = rooms;
      displayRooms(rooms);
      OFFSETS.push(currentOffset);
    }
  )
    .fail(() => {
      displayRooms(currentOffset.oldRooms);
      OFFSETS.push(currentOffset);
    });
}

var oldWeather;
function loadWeather() {
  $.getJSON(WEATHER_API, updateWeather)
    .fail(function () {
      updateWeather(oldWeather);
    });
}
function updateWeather(weather) {
  oldWeather = weather;
  var condition = weather.condition;
  var forecasts = weather.forecast;
  $("#today-temp").html(condition.temp + "&deg;");
  var conditions = [$("#today-condition"), $("#tomorrow-condition"), $("#daft-condition")];
  var lows = [$("#today-low"), $("#tomorrow-low"), $("#daft-low")];
  var highs = [$("#today-high"), $("#tomorrow-high"), $("#daft-high")];
  for (var i = 0; i < 3; i++) {
    var forecast = forecasts[i];
    lows[i].html("L " + forecast.low + "&deg;");
    highs[i].html("H " + forecast.high + "&deg;");
    conditions[i].attr("class", "wi wi-" + WEATHER_CODES[forecast.code]);
  }
  $("#daft").text(forecasts[2].day);
}

function updateClock() {
  var currentTime = new Date();
  var currentSeconds = currentTime.getSeconds();
  currentSeconds = (currentSeconds < 10 ? "0" : "") + currentSeconds;
  var minutesAndHours = formatAMPM(currentTime).split(" ");
  var timeOfDay = minutesAndHours[1];
  var currentTimeString = minutesAndHours[0] + ":" + currentSeconds;
  var hour = currentTimeString.split(":")[0];
  if (hour.length < 2) {
    currentTimeString = " " + currentTimeString;
  }
  $("#clock").text(currentTimeString);
  $("#ampm").text(timeOfDay);
  var options = {
    weekday: "long", year: "numeric", month: "long",
    day: "numeric"
  };
  $("#date").html(currentTime.toLocaleDateString("en-us", options));

  setTimeout(updateClock, 1000 - (currentTime.getTime() % 1000));
}

$(document).ready(function () {
  loadTable();
  setInterval(loadTable, 1000);
  loadWeather();
  setInterval(loadWeather, 10000);
  updateClock();
  loadTicker();
  setInterval(loadTicker, 1000); //Checks for changes in the announcements

  setInterval(function () {
    $.get(PAGE_VERSION + "?random=" + Math.random(), function (data) {
      if (pageVersion !== data) {
        location.reload(true);
      }
    });
  }, 60 * 60 * 1000);
  $.get(PAGE_VERSION, function (data) {
    pageVersion = data;
  });
});
