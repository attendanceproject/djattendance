const get_section_data = (elem) => {
  elem = $(elem);
  // Extract instructions and section type
  const instructions = elem.find("[name='section_instructions']").val();
  const section_id = elem.find("input[name=section_id]").val();
  const section_type = elem.find("select[name=section_type]").val();
  const required_number_to_submit = elem.find("[name=required_number_to_submit]").val();
  let questions = [];
  $.each(elem.find(".exam_question"), (e, v) => {
    questions.push(get_question_data(v, section_type));
  });
  return {
    instructions,
    section_id,
    section_type,
    required_number_to_submit,
    questions,
  };
};

const get_question_data = (elem, section_type) => {
  let obj = {};
  // Extract question data
  elem = $(elem);
  const container = elem.clone();
  const question_data = $('<form>').append(container).serializeArray();
  for (var i=0; i<question_data.length; i++) {
    var key = question_data[i].name;
    var val = question_data[i].value;
    obj[key] = val;
  }
  if (section_type == "TF") {
    obj["answer"] = elem.find("label.active input").val();
  }
  return obj;
};

$(() => {
  $("#exam-submit").click(e => {
    e.preventDefault();
    let rtn_data = {};

    // Add exam metadata
    const exam_metadata = $('.form-horizontal[name=exam_metadata]');
    const metadata_container = $(exam_metadata).clone();
    const metadata = $('<form>').append(metadata_container).serializeArray();

    let mtd = {};
    metadata.forEach(e => mtd[e.name] = e.value);
    mtd['training_class'] = $("#id_training_class").val();
    rtn_data['metadata'] = mtd;

    const question_data = $('.exam_question');
    rtn_data.sections = [];
    // Get section data for each section
    $.each($('.section'), (e, v) => {
      const section_data = get_section_data(v);
      if (section_data['questions'].length !== 0) {
        rtn_data.sections.push(section_data);
      }
    });

    $.ajax({
      type: 'POST',
      url: window.location.pathname,
      data: JSON.stringify(rtn_data),
      success: function(data, status, jqXHR) {
        if (data.ok) {
          window.location = SUCCESS_URL || window.location;
        } else {
          alert('Error saving exam: ' + data.msg);
        }
      },
      error: function (jqXHR, textStatus, errorThrown ) {
        alert('Error saving exam!');
      }
    });
  });
});
