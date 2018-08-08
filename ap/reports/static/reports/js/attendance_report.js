const averageHeaders = ["unexcused_absences_percentage", "sickness_percentage", "tardy_percentage", "classes_missed_percentage"];
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

// adjust the record made for localities and adjust it for teams by changing the serving teams to sending localities
function appendTeam(constructedRow, traineeInfo){
  const locId = traineeInfo["sending_locality"];
  const locality = $("#locality-"+locId).prev().children().first().text();
  let col = constructedRow.children.item(3);
  col.innerHTML = locality;

  const tableId = "team-" + traineeInfo["team"];
  $("#"+tableId).children("tbody").append(constructedRow);

}

// making a a single row record of HTML to append first for localities by listing only the serving teams
function appendResponse(traineeInfo){
  let traineeRecord = document.createElement("tr");
  const columnHeaders = ["name", "ta", "term", "team", "gender", "unexcused_absences_percentage", "tardy_percentage", "sickness_percentage", "classes_missed_percentage"];

  for (let i = 0; i< columnHeaders.length; i++){
    let col = document.createElement("td");
    col.innerHTML = traineeInfo[columnHeaders[i]];
    traineeRecord.append(col);
  }

  const tableId = "locality-" + traineeInfo["sending_locality"];
  $("#"+tableId).children("tbody").append(traineeRecord);

  appendTeam(traineeRecord.cloneNode(true), traineeInfo);

}

// single ajax request for a single trainee based upon trainee id
// using this to do parallel processing for trainee information by utilizing client-server infrastructure
function getTraineeRecord(traineeId, url){
  $.ajax({
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
          };

          // once all the ajax requests are completed, compute the averages and render it
          // also show the content of the now completed attendance report
          if (attendanceRecords.length === traineeIds.length){
            let list = document.createElement("ul");

            for (let i = 0; i < averageHeaders.length; i++) {
              let item = document.createElement("li");
              let avgValue = (Math.round((averageValues[i] / attendanceRecords.length) * 100) / 100).toFixed(2) + "%";
              returnAverageValues[averageHeaders[i]] = avgValue;
              item.innerHTML = averageHeaders[i] + ": " + avgValue;
              list.append(item);

            };

            $("#averages").append(list);

            $("#navigation_bar").show();
            $(".tab-content").show();
            $(".progress-bar").removeClass("active");
          }
        },
      });
}

function getAttendanceRecord(ids, url){
  traineeIds = ids;

  // define headers and computed values to calculate averages
  for (let i =0; i<averageHeaders.length; i++){
    averageValues.push(0);
  }

  traineeIds.forEach(function(element) {
    getTraineeRecord(element, url);
  });
}