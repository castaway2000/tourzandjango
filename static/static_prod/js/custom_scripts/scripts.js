$(document).ready(function(){

    function selectingHours(hours){
        $('#booking_hours option').attr('selected', false);
        $('#booking_hours option[value="'+hours+'"]').attr('selected','selected');
    };

    function priceCalculation(){
        var form = $('#form_tour_scheduling');
        var hours = form.find('.btn-group-select-num label.active input').val();
        var hourly_rate = form.find('#hourly_rate').val();

        if (hours>0){
            console.log("hours");
            selectingHours(hours);
        }else{
            hours = $('#booking_hours option:selected').val();
        }

        console.log("hours "+hours);
        console.log(hourly_rate);

        var total_amount = hours*hourly_rate;
        console.log(total_amount);
        $('#amount').text(total_amount);
        if ($('#amount_container').hasClass('hidden')){
            console.log('yes');
            $('#amount_container').removeClass('hidden');
        }else{
            console.log('no');
        }
    };

    $(document).on('click', '.hours-nmb', function(){
        $('#form_tour_scheduling .hours-nmb').removeClass('active');
        $(this).addClass('active');
        priceCalculation();
    });

    $(document).on('change', '#booking_hours', function(){
        priceCalculation();
    });


    function gettingFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });

        return indexed_array;
    };


    function hidingNotification(){
         window.setTimeout(function() {
            $('.booking-result-message').addClass('hidden');
         }, 2500);
    };


    //$('#form_tour_scheduling').on('submit', function(e){
    $('#form_guide_scheduling').on('submit', function(e){
        if ($(this).hasClass('user-not-authorized')){

        }else{
            e.preventDefault();
            console.log();
            var form = $(this);
            data = gettingFormData(form);

            var csrf_token = $('#csrf_getting_form [name="csrfmiddlewaretoken"]').val();
            data["csrfmiddlewaretoken"] = csrf_token;

            console.log(data);
            console.log("123");
            var url = form.attr("action");
            console.log(url);

            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                cache: true,
                success: function (data) {
                    console.log(data);
                    if (data.status == "success"){

                        $('.booking-result-message')
                            .removeClass('alert-danger hidden').addClass('alert-success');
                        $('.booking-result-message .message-text').text(data.message);

                        hidingNotification();

                    }else{
                        $('.booking-result-message')
                            .removeClass('alert-success hidden').addClass('alert-danger');
                        $('.booking-result-message .message-text').text("Failed");

                        hidingNotification();
                    }
                },
                error: function(){
                    $('.booking-result-message')
                            .removeClass('alert-success hidden').addClass('alert-danger');

                    $('.booking-result-message .message-text').text("Failed");
                }
            })
        }
    });

    $(document).on('click', '.close-alert', function(){
        $(this).closest('.booking-result-message').addClass('hidden');
    });


    priceCalculation();


    $('.change-language-link').on('click', function (e) {
        e.preventDefault();
        console.log("clicked");
        url = $(this).attr("href");
        window.location.href = url;
    });

    function changingPaymentType(){
        var current_payment_type = $('#payment_type').val();
        console.log(current_payment_type);
        if (current_payment_type == 1){
            $('#hourly_area').removeClass('hidden');
            $('#fixed_area').addClass('hidden');
        }else if (current_payment_type == 2){
            $('#hourly_area').addClass('hidden');
            $('#fixed_area').removeClass('hidden');
        }else{
            $('#hourly_area').addClass('hidden');
            $('#fixed_area').addClass('hidden');
        }
    }

    $(document).on('change', '#payment_type', function(){
        console.log("change");
        changingPaymentType();
    });

    changingPaymentType();


    $('#book_more').on('click', function(e){
        e.preventDefault();
        $('#booking_form_area').removeClass('hidden');
    });

});

$('.datepicker').datepicker();

//$('.datepicker.today-date').datepicker('setDate', 'today');
//

window.setTimeout(function() {
  $(".alert:not(.booking-result-message)").fadeTo(100, 0).slideUp(100, function(){
    $(this).addClass('hidden');
  });
}, 2500);
