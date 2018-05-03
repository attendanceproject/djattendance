/**
 * setup JQuery's AJAX methods to setup CSRF token in the request before sending it off.
 * http://stackoverflow.com/questions/5100539/django-csrf-check-failing-with-an-ajax-post-request
 */
function getCookie(name)
{
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

class Notification {
  constructor(type, text) {
    this.type = type;
    this.text = text;
  }

  set type(t) {
    this.alert = $('#notification_success');
    if (t == Notification.ERROR) {
      this.alert = $('#notification_error');
    }
  }

  static hideAll() {
    $('.notification').hide();
  }

  show() {
    Notification.hideAll();
    this.alert.find('.notification-content').html(this.text);
    this.alert.fadeIn()
      .css({top: 0})
      .animate({top: '20px'}, 500, () => {});
    setTimeout(() => {this.alert.fadeOut(1000); }, 3000);
    return this;
  }
}
Notification.ERROR = 'E';
Notification.SUCCESS = 'S';
window.Notification = Notification;

window.ajaxify = (elements, onSuccess=()=>{}) => {
  $(elements).click((e) => {
    e.preventDefault();
    $.ajax({
      url: e.currentTarget.href,
      type: "GET",
      success: (data, textStatus, xhr) => {
        onSuccess(e.currentTarget, data);
      },
      error: (jXHR, textStatus, errorThrown) => {
        alert(errorThrown);
      }
    });
  });
}

$(document).ready(function() {
  $('.notification-dismiss').on('click', (e) => {
    $(e.currentTarget).parent().fadeOut();
  });

  // Makes all textarea elastic (resize according to content)
  autosize($('textarea'));
  // Initialize the code that does the navbar stuff
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });

  let jqXhr = $.ajaxSettings.xhr;
  let $ajaxHR = $('#ajaxStatus');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    },
    xhr: function() {
      let xhr = jqXhr();
      xhr.upload.onprogress = evt => {
        $ajaxHR.show();
      }
      xhr.upload.onloadend = () => {
        $ajaxHR.animate({'width': '100%'}, 'slow', null, () => {
          $ajaxHR.fadeOut();
          $ajaxHR.css({'width': '0'});
        });
      };
      return xhr;
    },
  });
});
