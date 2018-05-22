$(document).ready(function() {

    function scrolling(scrolling_speed) {
        console.log("scrolling");
        if (scrolling_speed == undefined){
            scrolling_speed = 300;
        }
        //scroll down messaging area
        var scroll_container = $('#messages_area');
        scroll_container.animate({ scrollTop: scroll_container.prop('scrollHeight') }, scrolling_speed);
        console.log("scrolled")
    }

    var roomName = $("#chat_uuid").val();

    var chatSocket = new WebSocket(
        'ws://' + window.location.host +
        '/ws/chat/' + roomName + '/');

    chatSocket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        $('#messages_area').append('<div class="chat-message small">' +
                        '<div class="message-meta-info">' + data.user+ ', ' + data.dt + '</div>' +
                        '<div class="chat-message-text">' + data.message + '</div>' +
                        '</div>');
        scrolling();
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    var message_textarea = $('#message_textarea');
    message_textarea.focus();
    message_textarea.on("keyup", function(e) {
        if (e.keyCode === 13) {  // enter, return
            $('#chat_message_form').submit();
        }
    });

    $('#chat_message_form').on("submit", function(e) {
        e.preventDefault();
        var message = $('#message_textarea').val();
        var chat_uuid = $('#chat_uuid').val();
        chatSocket.send(JSON.stringify({
            'chat_uuid': chat_uuid,
            'message': message
        }));
        $('#message_textarea').val("");
    });

    scrolling(scrolling_speed=0);
    //End of chats area
});