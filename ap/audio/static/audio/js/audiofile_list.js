class AudioList {
  constructor() {
    this.audioItems = $('.audio-item');
  }
}

$(document).ready(() => {
  $('#week-select')
  .select2({
    data: WEEKS,
    minimumResultsForSearch: -1,
  })
  .val(WEEK)
  .trigger('change')
  .on('change', (e) => {
    window.location = AUDIO_LIST_URL.replace(URL_PLACEHOLDER, e.target.value);
  });

  // List item scripts
  let player = new AudioPlayer($('#player'));
  let audioList = new AudioList();
  audioList.audioItems.on('click', (e) => {
    let panel = e.currentTarget;
    player.playAudio(panel.getAttribute('src'));
    audioList.audioItems.removeClass('panel-primary');
    $(panel).removeClass('panel-default');
    $(panel).addClass('panel-primary');
  });

  $('.download-button').click((e) => {
    $(e.target).parent().parent().parent().parent().find('.panel-body').toggle();
    e.stopPropagation();
  });

  $('.download-link').click((e) => {
    e.stopPropagation();
  });

  $('.classnotes-button').click((e) => {
    e.stopPropagation();
  });
});
