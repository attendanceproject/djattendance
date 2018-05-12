$(document).ready(function() {
  $('.datetimepicker').datetimepicker({
    format:'m/d/Y g:i A',
    ampm: true,
    step: 30,
    validateOnBlur: false
  });
});
