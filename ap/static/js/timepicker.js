$(document).ready(function() {
  $(".timepicker").datetimepicker({
    format: "g:i A",
    formatTime: "g:i A",
    ampm: true,
    step: 30,
    defaultSelect: false,
    allowBlank: false,
    validateOnBlur: false,
    datepicker:false,
  });
});
