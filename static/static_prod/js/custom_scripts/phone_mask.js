$('#phone').intlTelInput({
    hiddenInput: "phone_formatted",
    formatOnDisplay: "auto",
    autoPlaceholder: "off",
    separateDialCode: true,
    initialCountry: "auto",
    geoIpLookup: function(callback) {
      $.get("https://ipinfo.io", function() {}, "jsonp").always(function(resp) {
        var countryCode = (resp && resp.country) ? resp.country : "";
        callback(countryCode);
      });
    },

    utilsScript: "/static/plugins/intl-tel-input/js/utils.js"

});


var phone_masks_data_url = "/static/plugins/data_for_phone_mask/country_phone_masks.json";
function gettingPhoneMasksData(callback){
    $.get(phone_masks_data_url, function(){}).always(function(data) {
        callback($.parseJSON(data));
    });
}

var phone_masks_data;
gettingPhoneMasksData(function(returned_data){ //anonymous callback function
    phone_masks_data = returned_data;
});



$("#phone").on("countrychange", function(e, country_data) {
    country = country_data.iso2.toUpperCase();
    dial_code = country_data.dialCode;

    //if country in the dictionary of countries, add mask and placeholder
    if (country in phone_masks_data){
         mask_format = phone_masks_data[country];

        //deleting country dial code which is already inside selected country and adding a bracket with a space
        mask_format_mod = mask_format.split(dial_code)[1];
        mask_format_mod = mask_format_mod.replace(')', ') ');

        var mask_options = {
            selectOnFocus: true,
            placeholder: mask_format_mod
        };
        $('#phone').mask(mask_format_mod, mask_options);
    }


});