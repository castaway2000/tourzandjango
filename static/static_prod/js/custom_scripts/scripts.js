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

    $('#form_tour_scheduling').on('submit', function(e){
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
                    if (data.status == "success"){
                        $('.booking-result-message')
                            .removeClass('alert-danger hidden').addClass('alert-success');
                        $('.booking-result-message .message-text').text(data.message);
                    }else{
                        $('.booking-result-message')
                            .removeClass('alert-success hidden').addClass('alert-danger');
                        $('.booking-result-message .message-text').text("Failed");
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


});

$('.datepicker').datepicker('setDate', 'today');


window.setTimeout(function() {
  $(".alert").fadeTo(100, 0).slideUp(100, function(){
    $(this).remove();
  });
}, 2000);
