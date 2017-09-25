$(document).ready(function(){

    function updatingChosenHours(){
        var form = $('.schedule-form');
        hours = $('#booking_hours:not(.hidden) option:selected').val();
        if (!hours){
            var hours = form.find('#hours_nmb_container .btn-group-select-num label.active input').val();
        }

        $('#booking_hours option').attr('selected', false);
        $('#booking_hours option[value="'+hours+'"]').attr('selected','selected');
        $('#booking_hours').val(hours);

        return hours
    };

    function priceCalculation(){

        updatingChosenHours();
        if ($('#amount_container').hasClass('hidden')){
            $('#amount_container').removeClass('hidden');
        }
    };

    $(document).on('click', '.hours-nmb', function(){
        //$('#form_tour_scheduling .hours-nmb').removeClass('active');
        $(this).parent().find('.hours-nmb').removeClass('active');
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
            //console.log(n['name']);
            //console.log(n['value']);
            //
            //indexed_array[n['name']] = n['value'];

            if (indexed_array[n['name']] ) {
                if ( typeof(indexed_array[n['name']]) === "string" ) {
                    indexed_array[n['name']] = [indexed_array[n['name']]];
                }
                indexed_array[n['name']].push(n['value']);
            } else {
                indexed_array[n['name']] = n['value'];
            }

        });

        return indexed_array;
    };


    function hidingNotification(){
         window.setTimeout(function() {
            $('.booking-result-message').addClass('hidden');
         }, 2500);
    };

    $('#form_guide_scheduling .submit-button, #form_tour_scheduling .submit-button').on('click', function(e){
        var booked_hours = updatingChosenHours();

        if (booked_hours>0){
            $('.schedule-form').find('#booking_hours').val(booked_hours);
        }

        $('#form_guide_scheduling').submit();

    });

    $(document).on('click', '.close-alert', function(){
        $(this).closest('.booking-result-message').addClass('hidden');
    });


    if ($('#amount_container').length > 0){
        priceCalculation();
    }



    $('.change-language-link').on('click', function (e) {
        e.preventDefault();
        url = $(this).attr("href");
        window.location.href = url;
    });

    function changingPaymentType(){
        var current_payment_type = $('#payment_type').val();
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
        changingPaymentType();
    });

    changingPaymentType();


    $('#book_more').on('click', function(e){
        e.preventDefault();
        $('#booking_form_area').removeClass('hidden');
        if ($('#additional_services_select').length>0){
            $('#booking_form_area #additional_services_select').select2({
                placeholder: 'Select additional services'
            });
        }
    });


    $(".btn-order-review").magnificPopup({
            type: 'inline', // set source type (image default)
            removalDelay: 500, // delay removal by X to allow out-animation,
            midClick: true, // Allow opening popup on middle mouse click. Always set it to true if you don't provide alternative source in href
            callbacks: {
                //beforeOpen: function(e) {
                //  // Set Magnific Animation
                //  var Animation = "mfp-rotateLeft";
                //  this.st.mainClass = Animation;
                //
                //  // Inform content container there is an animation
                //  this.contentContainer.addClass('mfp-with-anim');
                //},

                open: function(){

                    console.log("open");
                    var $triggerEl = $(this.st.el);
                    var order_id = $triggerEl.data("order_id");
                    console.log(order_id);

                    var self = $.magnificPopup.instance;
                    self.contentContainer.find('#order_id').val(order_id)

                }
            }
    });

    $(document).on('change', '.service-name-checkbox', function() {
        console.log("change");
        var current_row = $(this).closest('tr');
        console.log(current_row);
        current_row.find('.service-price').toggleClass('hidden');
    });


    function togglingEditingPhoneStuff(){
        $('#submit_phone_btn').toggleClass('hidden');
        $('#validate_phone_btn').toggleClass('hidden');
        $('#sms_code_container').toggleClass('hidden')
    };

    $('#edit_phone').on('click', function(){
        togglingEditingPhoneStuff();
    });


    //$('#submit_phone_btn').on('click', function(e){
    //    e.preventDefault();
    //
    //    var phone = $('#phone').val();
    //    console.log(phone);
    //    console.log(phone.length);
    //    if (phone.length < 7){
    //        $('#phone_error_message').text("Enter valid phone");
    //        return false;
    //    }
    //
    //    data = {};
    //    var csrf_token = $('#csrf_getting_form [name="csrfmiddlewaretoken"]').val();
    //    data["csrfmiddlewaretoken"] = csrf_token;
    //    data["phone"] = phone;
    //
    //
    //    var url = $(this).data('link');
    //    $.ajax({
    //         url: url,
    //         type: 'POST',
    //         data: data,
    //         cache: true,
    //         success: function (data) {
    //             console.log(data);
    //             if(data.status=='success'){
    //                 togglingEditingPhoneStuff();
    //             };
    //         }
    //    })
    //});


    $('#is_company').on("change", function(){
        if ($(this).prop("checked")){
            $('#business_id_container').removeClass("hidden");
        }else{
            $('#business_id_container').addClass("hidden");
        }
    })

});

$('.datepicker').datepicker();

//$('.datepicker.today-date').datepicker('setDate', 'today');
//

window.setTimeout(function() {
  $(".alert:not(.booking-result-message)").fadeTo(100, 0).slideUp(100, function(){
    $(this).addClass('hidden');
  });
}, 2500);


$(document).ready(function(){
    $(document).on('click', '#toggle_left_menu', function(e) {
        console.log("aa");
         if($.cookie("left_menu_hided") == 1) {
             $.cookie("left_menu_hided", 0, {path: '/'});
             console.log("set 0");
         }
         else{
            $.cookie("left_menu_hided", 1, {path: '/'});
             console.log("set 1");
        }
        hidingLeftMenu()
    });


});

function hidingLeftMenu(){
    if ($.cookie("left_menu_hided") == 1) {
        $('.booking-filters-container').addClass("closed");
        console.log("min");
    }else{
        $('.booking-filters-container').removeClass("closed");
        console.log("max");
    }
}
hidingLeftMenu();


//sticking leftbar on scroll

$(window).scroll(function () {
    var scroll = $(window).scrollTop();
    var width = $(window).width();
    elementsResizing()
});

function elementsResizing(){
    var scroll = $(window).scrollTop();
    var width = $(window).width();
    if (scroll >= 130 && width>990) {
        $('.booking-filters-container').addClass('sticky-top');
    } else  {
        $('.booking-filters-container').removeClass('sticky-top');
    };
    if (width>990){
        $('.booking-filters-container').removeClass("closed");
    }
};

$(window).resize(function () {
    elementsResizing();
});