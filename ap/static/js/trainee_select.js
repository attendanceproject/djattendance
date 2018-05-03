// data: array of trainee ids to be added into the Trainee field
// function selects trainees in Trainee Select2 field.
window.addTrainees = (trainee_ids) => {
  var curr = ($('#id_trainees').val());
  if (curr) {
    trainee_ids = [...new Set([...curr, ...trainee_ids])];
  }
  $('#id_trainees').val(trainee_ids).trigger('change');
  return;
}

$(document).ready(function() {
  $('body').append(TRAINEE_SELECT_MODAL_HTML);
  $('#id_team').djangoSelect2({width: '100%'});
  $('#id_house').djangoSelect2({width: '100%'});
  $('#id_locality').djangoSelect2({width: '100%'});

  var base_url = window.location.protocol + '//' + window.location.host;
  var api_base = '/api'


  function getTrainees(data) {
    var trainee_groups = {
      'terms': [],
      'gender': [],
      'hc': [],
      'team_types': [],
      'teams': [],
      'houses': [],
      'localities': []
    };

    var deferreds = []; // all ajax deferred objects get pushed into here

    for (i = 0; i < data['terms'].length; i++) {
      deferreds.push(
        $.ajax({
          url: base_url + api_base + '/trainees/term/' + data['terms'][i] + '/?format=json',
          contentType: 'application/json',
          data: data,
          dataType: 'json',
          success: function(data) {
            trainee_groups['terms'] = [...new Set([...trainee_groups['terms'], ...getTraineeIDs(data)])];
          }
        }));
    }

    if (data['gender']) {
      deferreds.push(
        $.ajax({
          url: base_url + api_base + '/trainees/gender/' + data['gender'] + '/?format=json',
          contentType: 'application/json',
          data: data,
          dataType: 'json',
          success: function(data) {
            trainee_groups['gender'] = getTraineeIDs(data);
          }
        }));
    }

    if (data['hc']) {
      deferreds.push(
        $.ajax({
          url: base_url + api_base + '/trainees/hc/?format=json',
          contentType: 'application/json',
          data: data,
          dataType: 'json',
          success: function(data) {
            trainee_groups['hc'] = getTraineeIDs(data);
          }
        }));
    }

    for (i = 0; i < data['team_types'].length; i++) {
      deferreds.push(
        $.ajax({
          url: base_url + api_base + '/trainees/teamtype/' + data['team_types'][i] + '/?format=json',
          contentType: 'application/json',
          data: data,
          dataType: 'json',
          success: function(data) {
            trainee_groups['team_types'] = [...new Set([...trainee_groups['team_types'], ...getTraineeIDs(data)])];
          }
        }));
    }

    if (data['teams']!==null) {
      for (i = 0; i < data['teams'].length; i++) {
        if(data['teams'][i] === "") continue;
        deferreds.push(
          $.ajax({
            url: base_url + api_base + '/trainees/team/' + data['teams'][i] + '/?format=json',
            contentType: 'application/json',
            data: data,
            dataType: 'json',
            success: function(data) {
              trainee_groups['teams'] = [...new Set([...trainee_groups['teams'], ...getTraineeIDs(data)])];
            }
          }));
      }
    }

    if (data['houses']!==null) {
      for (i = 0; i < data['houses'].length; i++) {
        if(data['houses'][i] === "") continue;
        deferreds.push(
          $.ajax({
            url: base_url + api_base + '/trainees/house/' + data['houses'][i] + '/?format=json',
            contentType: 'application/json',
            data: data,
            dataType: 'json',
            success: function(data) {
              trainee_groups['houses'] = [...new Set([...trainee_groups['houses'], ...getTraineeIDs(data)])];
            }
          }));
      }
    }

    if (data['localities']!==null) {
      for (i = 0; i < data['localities'].length; i++) {
        if(data['localities'][i] === "") continue;
        deferreds.push(
          $.ajax({
            url: base_url + api_base + '/trainees/locality/' + data['localities'][i] + '/?format=json',
            contentType: 'application/json',
            data: data,
            dataType: 'json',
            success: function(data) {
              trainee_groups['localities'] = [...new Set([...trainee_groups['localities'], ...getTraineeIDs(data)])];
            }
          }));
      }
    }

    // when all ajax calls are successful, find intersection of
    // all trainee groups and add trainees to Trainee field.
    $.when.apply($, deferreds).then(function(){
      var intersect = [];
      for (k in data) {
        if (data[k] != false && data[k] != undefined) {
          intersect.push(trainee_groups[k])
        }
      }
      if (intersect.length!==0) {
        window.addTrainees(intersect.reduce((arr1,arr2) => arr1.filter(x => new Set(arr2).has(x))));
      }
    });

  }

  // data: trainees in JSON
  // return array of trainee ids
  function getTraineeIDs(data) {
    var trainee_ids = [];
    for (i = 0; i < data.length; i++) {
      trainee_ids[trainee_ids.length] = data[i]['id'];
    };
    return trainee_ids;
  }

  $('#add_trainees').click(function(event) {
    event.preventDefault();
    form_data = {
      'terms': getValues($('input[name=term]:checked')),
      'gender': $('input[name=gender]:checked').attr('value'),
      'hc': $('#id_hc').is(":checked"),
      'team_types': getValues($('input[name=team_type]:checked')),
      'teams': $("#id_team").val(),
      'houses': $("#id_house").val(),
      'localities': $("#id_locality").val(),
    };
    getTrainees(form_data);
    clearForm();
    $('#trainee_select').modal('hide');
  });

  function getValues(object) {
    var values = [];
    object.each(function() {
      values[values.length] = $(this).attr('value');
    })
    return values;
  }

  function clearForm() {
    $('input:checkbox').removeAttr('checked');
    $('input:radio').removeAttr('checked');
    $('#id_team').select2().val(null).trigger('change');
    $('#id_house').select2().val(null).trigger('change');
    $('#id_locality').select2() .val(null).trigger('change');
  }
});
