const isFinalize = "Y";
const notFinalize = "N";

function disableButtons() {
    $("#save").prop("disabled", true);
    $("#finalize").prop("disabled", true);
    $(".btn-group label").attr("disabled", true);
    $(".btn-group :input").attr("disabled", true);

    // for homepage (index.html)
    $("#bt-button").prop("disabled", true);
    $(".bible-selector").prop("disabled", true);
}

function enableButtons() {
    $("#save").prop("disabled", false);
    $("#finalize").prop("disabled", false);
    $(".btn-group label").attr("disabled", false);
    $(".btn-group :input").attr("disabled", false);

    // for homepage (index.html)
    $("#bt-button").prop("disabled", false);
    $(".bible-selector").prop("disabled", false);
}

/****** functions exclusive for bible_tracker page ******/
function setWeeks() {
    var firstDayofWeek = moment(first_day_term, "YYYYMMDD");
    var lastDayofWeek = firstDayofWeek.clone().add(6, "days");
    for (var i = 0; i <= currentWeek; i++) {
        $("#week_select").append($("<option />").val(i).text("Week " + i + ": " + firstDayofWeek.format("ddd MMM D") + " - " + lastDayofWeek.format("ddd MMM D")).attr("id", i));
        firstDayofWeek = lastDayofWeek.add(1, "day");
        lastDayofWeek = firstDayofWeek.clone().add(6, "days");
    }
}

function setDatesforWeek(week) {
    enableButtons();
    var firstDay = moment(first_day_term, "YYYYMMDD");
    var firstDayofWeek = firstDay.add(week, "weeks");
    var WedofNextWeek = firstDayofWeek.clone().add(9, "days");
    var lastDayofWeek = firstDayofWeek.clone().add(6, "days");
    var currentDayofWeek = firstDayofWeek.clone();
    var now = moment();
    for (var i = 0; i < 7; i++) {
        $("#day-" + i).html(currentDayofWeek.format("ddd - MMM D"));
        currentDayofWeek.add(1, "days");
    }
    //finalize is disabled on Wednesday of next week (with HH:mm of 00:00) or before week is over (Sunday midnight+20 minutes)
    if (isTrainee && (/*now > WedofNextWeek || */now < lastDayofWeek.clone().add(20, "minutes"))) {
        $("#finalize").prop("disabled", true);
    }
    //save button is disabled for more than this week"s Bible reading
    if (isTrainee && lastDayofWeek >= now.clone().add(6, "days")) {
        $("#save").prop("disabled", true);
    }
}

function modifyBoxes(classname) {
    var x = document.getElementsByClassName(classname)[0];
    x.setAttribute("checked", "true");
}

function updateProgressBar(selector, data) {
    $(selector).css("width", data + "%");
    $(selector).html(data + "%");
    $(selector).attr("aria-valuenow", data);
}

function unfinalizeStatus() {
    var weekId = $("#week_select").find(":selected").attr("id");
    var userId = $("input#userId").val();

    $.ajax({
        type: "POST",
        url: finalizeStatusUrl,
        data: {
            "week_id": weekId,
            "action": "unfinalize",
            "userId": userId,
        },
        success: function (data) {
            enableButtons();
            $("#unfinalize").prop("disabled", true);
        },// success
        error: function (data) {
            alert("Sorry, there was an error processing this request."); // <- this should run if user is not activated
        } // error
    });
}

function toggleCheckbox(classname, id, year) {
    var checked = document.getElementsByClassName(classname)[0].checked;
    var userId = $("input#userId").val();

    $.ajax({
        type: "POST",
        url: updateBooksUrl,
        data: {
            "book": id,
            "year": year,
            "checked": checked,
            "userId": userId,
        },
        success: function (data) {
            let text = checked ? "Saved" : "Deleted";
            new Notification(Notification.SUCCESS, text).show();
            if (year === 1) {
                updateProgressBar("#first-year-prog", data);
            } else if (year === 2) {
                updateProgressBar("#second-year-prog", data);
            }
        }
    });
}

function getStatus() {
    var weeklyStatus = "";
    for (var i = 0; i < 7; i++) {
        var dayStatus = $("#status-day-" + i + " label.active input").val();
        if (dayStatus == null) {
            weeklyStatus += "_";
        }
        else {
            weeklyStatus += dayStatus;
        }
    }
    return weeklyStatus;
}

/****** functions exclusive for homepage (index.html) ******/
function checkBibleReadingStatus() {
    return (bibleReadingStatus.match(/_/g) ? true : false);
}

function changetoFinalize() {
    // check if bible reading for the week is already finalized
    if (finalized === isFinalize) {
        $("#bt-button").val("Finalize");
        disableButtons();
    }

    var timeNow = moment();
    var start = moment().day(0).hours(0).minutes(20).seconds(0);
    var end = moment().day(2).hours(23).minutes(59).seconds(59);

    // check bible reading values
    if (!checkBibleReadingStatus()) {
        // check if date is valid for user if they can finalize (from Lord"s Day to Tuesday)
        if (moment(timeNow).isBetween(start, end, "second")) {
            $("#bt-button").val("Finalize");
        }
    }
    else {
        $("#bt-button").val("Save");
    }
}

function getWeeklyStatus() {
    var code = bibleReadingStatus.split("");

    for (let i = 0; i < 7; i++) {
        document.getElementById("bibleDropDown_" + weekdayCodes[i]).value = code[i];
    }
}

/****** functions used in index and bible_tracker page ******/
function changeWeek() {
    var weekId = $("#week_select").val();
    var userId = $("input#userId").val();
    var url = "/bible_tracker/?week=" + weekId;
    history.pushState({ urlPath: url }, "", url);
    $(".btn.btn-primary.active").removeClass("active");

    $.ajax({
        type: "GET",
        url: changeWeekUrl,
        dataType: "json",
        data: {
            "week": weekId,
            "userId": userId,
            "forced": forced,
        },
        success: function (data) {
            var obj = JSON.parse(data);
            var status = obj.status;
            var finalized = obj.finalized;

            setDatesforWeek(parseInt(weekId));
            var res = status.split("");
            for (var i = 0; i < res.length; i++) {
                $("#status-day-" + i).find("input#" + res[i]).parent().addClass("active");
            }
            if (finalized === isFinalize) {
                $("#unfinalize").prop("disabled", false);
                disableButtons();
            }
            if (finalized === notFinalize) {
                $("#save").prop("disabled", false);
                $(".btn-group label").attr("disabled", false);
                $(".btn-group :input").attr("disabled", false);
                $("#unfinalize").prop("disabled", true);
            }

            if (forced == "True") {
                $("#finalize").prop("disabled", false);
            }
        },
    });
}

// Changing the week reloads the table to load the bible reading status of that week
function changeHomepageWeek() {
    var weekId = $("#week-select").val();
    currentWeek = weekId;

    $.ajax({
        type: "GET",
        url: changeWeekUrl,
        dataType: "json",
        data: {
            "week": weekId,
        },
        success: function (data) {
            var obj = JSON.parse(data);
            bibleReadingStatus = obj.status;
            finalized = obj.finalized;

            getWeeklyStatus();
            changetoFinalize();

            if (finalized === isFinalize) {
                disableButtons();
            }
            else {
                enableButtons();
            }
        }
    });
}

function updateStatus(finalize) {
    var weeklyStatus = getStatus();
    var weekId = $("#week_select").find(":selected").attr("id");
    var userId = $("input#userId").val();
    $.ajax({
        type: "POST",
        url: updateStatusUrl,
        data: {
            "week_id": weekId,
            "weekly_status": weeklyStatus,
            "userId": userId,
        },
        success: function (data) {
            if (finalize) {
                finalizeStatus();
            }
            new Notification(Notification.SUCCESS, "Saved").show();
        },
    });
}

function updateStatusFromHomepage(finalize) {
    var weeklyStatus = "";

    for (var i = 0; i < 7; i++) {
        var dayStatus = $("#bibleDropDown_" + weekdayCodes[i]).val();

        if (dayStatus === " " || dayStatus === null) {
            weeklyStatus += "_";
        }
        else {
            weeklyStatus += dayStatus;
        }
    }
    bibleReadingStatus = weeklyStatus;

    $.ajax({
        type: "POST",
        url: updateStatusUrl,
        data: {
            "week_id": currentWeek,
            "weekly_status": bibleReadingStatus,
        },
        success: function (data) {
            new Notification(Notification.SUCCESS, "Saved").show();
        },
    });

    changetoFinalize();
}

function finalizeStatus() {
    var confirmed = confirm("Are you sure you want to finalize bible reading for this week? You will not be able to edit afterwards.");
    if (confirmed) {
        var weekId = $("#week_select").find(":selected").attr("id");
        var userId = $("input#userId").val();
        $.ajax({
            type: "POST",
            url: finalizeStatusUrl,
            data: {
                "week_id": weekId,
                "action": "finalize",
                "userId": userId,
                "forced": forced,
            },
            success: function (data) {
                new Notification(Notification.SUCCESS, "Finalized").show();
                disableButtons();
                $("#unfinalize").prop("disabled", false);
            },
            error: function (data) {
                alert("Cannot finalize at this time");
            }
        });
    } else {
        //makes sure button does not stay pressed
        $("#finalize").blur();
    }
}

function finalizeStatusFromHomepage() {
    var weekId = document.getElementById("week_select").value;
    var confirmed = confirm("Are you sure you want to finalize bible reading for this week? You will not be able to edit afterwards.");
    if (confirmed) {

        $.ajax({
            type: "POST",
            url: finalizeStatusUrl,
            data: {
                "week_id": weekId,
                "action": "finalize",
            },
            success: function (data) {
                new Notification(Notification.SUCCESS, "Finalized").show();
                disableButtons();
            },
            error: function (data) {
                alert("Cannot finalize at this time");
            }
        });
    } else {
        //makes sure button does not stay pressed
        $("#bt-button").blur();
    }
}
