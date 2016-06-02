  (function () {
    var $container = $('#containerFor{{object.pk}}');

  var hasCustomFee = function() {
    return $container.find('#fee_override_account_group_spread_exists_true').is(':checked');
  };

  var setFeeSum = function() {
    var fee = parseInt($container.find('.platform-fee').text());

    if (hasCustomFee()) {
      fee += parseInt($container.find('.custom-fee').val() || '0');
    } else {
      fee += parseInt($container.find('.advised-fee').text());
    }

    if (isNaN(fee)) {
      fee = '-';
    }

    $container.find('.total-fee').text(fee.toString());
  };

  $container.html('{{html_output}}');

  setFeeSum();

  $container.find("#fee_override_account_group_spread_exists_true, #fee_override_account_group_spread_exists_false").on("change", function() {
    setFeeSum();
  });

  $container.find(".custom-fee").on("keyup", function() {
    setFeeSum();
  });

  $container.find(".custom-fee").on("focus", function() {
    $('#fee_override_account_group_spread_exists_true').prop('checked', true);
  });

  $container.find('.form-buttons a.close').click(function() {
    $container.html('');
    return false;
  });

  })();

