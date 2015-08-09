(function(window, $){
  var $alertBox;
  $(window).on('load', function () {
    $alertBox = $('[data-module="alert-box"]');
  });
  
  window.flash = function(msg) {
    var html = '<div class="row">'+
               '  <div class="alert alert-warning alert-dismissible" role="alert" data-module="alert-box">'+
               '    <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
                    msg +
               '  </div>'+
               '</div>';
    $alertBox.append(html);
  };

}(window, jQuery));
