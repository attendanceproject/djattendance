const averageHeaders = ["unexcused_absences_percentage", "sickness_percentage", "tardy_percentage", "classes_missed_percentage"];
let localitiesJson = {};
let attendanceRecords = [];
let traineeIds = [];
let averageValues = [];
let returnAverageValues = {};

function getAverageValues(){
  return returnAverageValues;
}

// dynamically adjust the progress bar as ajax requets are being completed
function updateProgress(){
  const computedPercentage = Math.round(attendanceRecords.length / traineeIds.length * 100);
  $("#progressbar").children().attr("aria-valuenow", computedPercentage).css("width", computedPercentage + "%").text(computedPercentage + "% Complete");
}

// making a a single row record of HTML to append first for localities by listing only the serving teams
function appendResponse(traineeInfo){
  let traineeRecord = document.createElement("tr");
  const columnHeaders = ["name", "ta", "term", "sending_locality", "team", "gender", "unexcused_absences_percentage", "tardy_percentage", "sickness_percentage", "classes_missed_percentage"];

  for (let i = 0; i< columnHeaders.length; i++){
    let col = document.createElement("td");
    let data = traineeInfo[columnHeaders[i]];
    if (columnHeaders[i] === "sending_locality"){
      data = localitiesJson[data];
    }
    col.innerHTML = data;
    traineeRecord.append(col);
  }

  let noTeamRecord = traineeRecord.cloneNode(true);
  noTeamRecord.children.item(4).remove();

  let noLocRecord = traineeRecord.cloneNode(true);
  noLocRecord.children.item(3).remove();

  const summaryTableId = "summary-table";
  $("#"+summaryTableId).children("tbody").append(traineeRecord);

  const tableId = "locality-" + traineeInfo["sending_locality"];
  $("#"+tableId).children("tbody").append(noTeamRecord);

  const teamTableId = "team-" + traineeInfo["team"];
  $("#"+teamTableId).children("tbody").append(noLocRecord);

}

function finishRendering() {
  // once all the ajax requests are completed, compute the averages and render it
  // also show the content of the now completed attendance report
  let list = document.createElement("ul");

  for (let i = 0; i < averageHeaders.length; i++) {
    let item = document.createElement("li");
    let avgValue = (Math.round((averageValues[i] / attendanceRecords.length) * 100) / 100).toFixed(2) + "%";
    returnAverageValues[averageHeaders[i]] = avgValue;
    item.innerHTML = averageHeaders[i] + ": " + avgValue;
    list.append(item);

  }

  $("#averages").append(list);
  $("#averages").show();
  $("#navigation_bar").show();
  $(".tab-content").show();
  $(".progress-bar").removeClass("active");

  $("#summary-table").DataTable({
    dom: '<"row"<"col-sm-6"Bl><"col-sm-6"f>>' +
    '<"row"<"col-sm-12"<"table-responsive"tr>>>' +
    '<"row"<"col-sm-5"i><"col-sm-7"p>>',
    buttons: [
      {
        extend: 'csvHtml5',
        text: 'CSV',
        exportOptions: {
          columns: ':visible'
        },
      },
    ],
  });
}

// single ajax request for a single trainee based upon trainee id
// using this to do parallel processing for trainee information by utilizing client-server infrastructure
function getTraineeRecord(traineeId, url){
  return $.ajax({
      type: "GET",
      url: url,
      data: {
        traineeId: traineeId,
      },
      success: function(response){
          attendanceRecords.push(response);
          appendResponse(response);
          updateProgress();

          // used for computing the averages by first obtaining the sum for each one
          for (let i = 0; i < averageHeaders.length; i++) {
            averageValues[i] = averageValues[i] + parseFloat(response[averageHeaders[i]]);
          }

          if (attendanceRecords.length === traineeIds.length){
            finishRendering();
          }
        },
      });
}

function runLoop(data, url) {
  var j = 0;

  function next() {
    if (j < data.length) {
      return getTraineeRecord(data[j], url).then(function(data) {
        ++j;
        return next();
      });
    } else {
      finishRendering();
    }
  }
  return next();
}


function getAttendanceRecord(ids, url){
  traineeIds = ids;  // redundant, but leaving it

  // define headers and computed values to calculate averages
  for (let i =0; i<averageHeaders.length; i++){
    averageValues.push(0);
  }

  traineeIds.forEach(function(element) {
    getTraineeRecord(element, url);
  });
  //runLoop(traineeIds, url);
}
