// ajax call to database for inline editing
function editDB(updated, rem_pk, field, url) {
  var pass = false;

  $.ajax({
    async: false,
    type: "POST",
    url: url,
    data: {
      change: updated,
      pk: rem_pk,
      f: field
    },
    success: function(response) {
      pass = true;
      new Notification(Notification.SUCCESS, 'Saved').show();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      new Notification(Notification.ERROR, errorThrown).show();
    }
  });

  return pass;
}

// set event for inline editing when you double click remembrance text or reference.
function tableInlineEdit(clicked, url) {
  var orig = clicked.text(); // for comparison
  if (orig == "None") {
    orig = "";
  }
  var input = $('<input>', {
    value: orig,
    type: 'text',
    blur: function() { // clicking outside box when editing is finished
      var passed = false;
      if (this.value != orig) {
        passed = editDB(this.value, clicked.parent().attr("id"), clicked.attr("class"), url); // id gives pk; class gives field changed; returns whether database successfully updated
      }

      if (passed) {
        clicked.text(this.value);
      } else {
        clicked.text(orig);
      }
    },
    keyup: function(e) { // if pressing enter
      if (e.which === 13) input.blur();
    }
  });

  input.appendTo( clicked.empty() ).focus();
}