$(document).ready(function() {

    function gettingFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });

        return indexed_array;
    };


    //Start of chats area
    function scrolling() {
        var scroll_container = $('#messages_area');
        var height = scroll_container[0].scrollHeight;
        scroll_container.scrollTop(height);
    };


    $('#chat_message_form').on('submit', function (e) {
        console.log("chat_message_form");

        e.preventDefault();
        var data = gettingFormData($(this));
        var url = $(this).attr("action");

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            cache: true,
            success: function (data) {
                if (data.message) {
                    $('#messages_area').append('<div class="chat-message small">' +
                        '<div class="message-meta-info">' + data.author + ', ' + data.created + '</div>' +
                        '<div class="chat-message-text">' + data.message + '</div>' +
                        '</div>');
                    $('#message_textarea').val("");
                    scrolling();
                }
            },
            error: function () {
                console.log("error");
            }
        })
    });
    scrolling();
    //End of chats area
});