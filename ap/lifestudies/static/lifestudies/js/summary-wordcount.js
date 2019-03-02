// Word counter for summary model
// First append the word count span
$().ready(function (){
  var minCount = $('#id_minimum_words').get(0).value;
  var content = $('#id_content');
  var wc_text = $(document.createElement('b')).html('Word Count: ');
  var wc_span = $(document.createElement('span')).html('0');
  wc_span.attr('id', 'count');

  content.after(wc_text)
  wc_text.after(wc_span);
  wc_span.after('<br />');

  Countable.on(content.get(0), function(counter){
    var span = $('#count').get(0);
    span.innerHTML = counter.words;
    $("#summary_submit").get(0).disabled = counter.words >= minCount ? false : true;
  })

  $("#id_submitting_paper_copy").click(function(){
    if (!$("#id_submitting_paper_copy").prop("checked")){
      $("#summary_submit").get(0).setAttribute("disabled", true);
    }else{
      $("#summary_submit").get(0).removeAttribute("disabled");
    }

  });
});
