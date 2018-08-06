let attendance_records = [];
//var date_from = "{{date_from}}";
//var date_to = "{{date_to}}";
let trainee_ids = [];

function getAttendanceRecord(ids, url){
  trainee_ids = ids;
  console.log(trainee_ids);
  console.log(ids);
  trainee_ids.forEach(function(element) {
    get_trainee_record(element, url);
  });
}

// define headers and computed values to calculate averages
let average_headers = ['unexcused_absences_percentage', 'sickness_percentage', 'tardy_percentage', 'classes_missed_percentage'];
let average_values = []
for (let i =0; i<average_headers.length; i++){
  average_values.push(0);
}

// dynamically adjust the progress bar as ajax requets are being completed
function update_progress(){
  let compute_percentage = Math.round(attendance_records.length / trainee_ids.length * 100);
  $("#progressbar").children().attr("aria-valuenow", compute_percentage).css("width", compute_percentage + "%").text(compute_percentage + "% Complete");
}

// making a a single row record of HTML to append first for localities by listing only the serving teams
function append_response(trainee_info){
  let trainee_record = document.createElement("tr");
  let column_headers = ["name", "ta", "term", "team", "gender", "unexcused_absences_percentage", "tardy_percentage", "sickness_percentage", "classes_missed_percentage"]

  for (let i = 0; i< column_headers.length; i++){
    let col = document.createElement("td");
    col.innerHTML = trainee_info[column_headers[i]];
    trainee_record.append(col);
  }

  table_id = "locality-" + trainee_info["sending_locality"];
  $("#"+table_id).children("tbody").append(trainee_record);

  append_team(trainee_record.cloneNode(true), trainee_info);

}

// adjust the record made for localities and adjust it for teams by changing the serving teams to sending localities
function append_team(constructed_row, trainee_info){
  l_id = trainee_info["sending_locality"];
  locality = $("#locality-"+l_id).prev().children().first().text();
  col = constructed_row.children.item(3);
  col.innerHTML = locality;

  table_id = "team-" + trainee_info["team"];
  $("#"+table_id).children("tbody").append(constructed_row);

}

function send_averages(){
}

// single ajax request for a single trainee based upon trainee id
// using this to do parallel processing for trainee information by utilizing client-server infrastructure
function get_trainee_record(trainee_id, url){
  $.ajax({
      type: "GET",
      url: url,
      data: {
        t_id: trainee_id,
      },
      success: function(response){
          attendance_records.push(response);
          append_response(response);
          update_progress();

          // used for computing the averages by first obtaining the sum for each one
          for (let i = 0; i < average_headers.length; i++) {
            average_values[i] = average_values[i] + parseFloat(response[average_headers[i]]);
          };

          // once all the ajax requests are completed, compute the averages and render it
          // also show the content of the now completed attendance report
          if (attendance_records.length == trainee_ids.length){
            let list = document.createElement("ul");

            for (let i = 0; i < average_headers.length; i++) {
              let item = document.createElement("li");
              avg_value = (Math.round((average_values[i] / attendance_records.length) * 100) / 100).toFixed(2) + "%";
              item.innerHTML = average_headers[i] + ": " + avg_value;
              list.append(item);

            };

            $("#averages").append(list);
            send_averages();

            console.log("complete");
            $("#navigation_bar").show();
            $(".tab-content").show();
            $(".progress-bar").removeClass("active");
          }
        },
      })
};