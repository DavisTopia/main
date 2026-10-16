jQuery(document).ready(function() {
  jQuery('.fc-form').each(function(){
    form = jQuery(this);
    var key = form.find('.captcha-placeholder').attr('data-site-key');
    if (typeof key !== 'undefined' && key !== '' && window.fc_reCaptcha !== true) {
      jQuery.getScript('https://www.google.com/recaptcha/api.js?render='+key);
      window.fc_reCaptcha = true
    }
  });

  jQuery(document).bind('formcraft_submit_trigger', function(event, form, data, abort) {
    var key = form.find('.captcha-placeholder').attr('data-site-key');
    var token = form.find('.recaptcha-token').val();
    if (form.find('.recaptcha-token').length === 0) {
      return
    }
    if (token === '' || typeof token === 'undefined') {
      abort.abort = true;
      grecaptcha.ready(function() {
        grecaptcha.execute(key, { action: 'submit' }).then(function(token) {
          form.find('.recaptcha-token').val(token);
          form.find('.submit-button').prop('disabled', false);
          form.find('.submit-cover').removeClass('disabled');
          FormCraftSubmitForm(form, 'all');
        });
      });
    }
  }); 

  jQuery(document).bind('formcraft_submit_success_trigger', function(event, form, response) {
    form.find('.recaptcha-token').val('');
  });     
})