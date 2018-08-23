$(document).ready(function() {

    function scrolling(scrolling_speed) {
        if (scrolling_speed == undefined){
            scrolling_speed = 300;
        }
        //scroll down messaging area
        var scroll_container = $('#messages_area');
        scroll_container.animate({ scrollTop: scroll_container.prop('scrollHeight') }, scrolling_speed);
    }

    var roomName = $("#chat_uuid").val();

   function connect() {
     console.log("connecting");
     var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
     var url = ws_scheme+ '://' + window.location.host +
        '/ws/chat/' + roomName + '/';

      var ws = new WebSocket(url);
      ws.onopen = function() {
        // subscribe to some channels
        //ws.send(JSON.stringify({
        //    //.... some message the I must send when I connect ....
        //}));
      };

      ws.onmessage = function(e) {
        var data = JSON.parse(e.data);
        $('#messages_area').append('<div class="chat-message small new-chat-message">' +
                        '<div class="message-meta-info">' + data.user+ ', ' + data.dt + '</div>' +
                        '<div class="chat-message-text">' + data.message + '</div>' +
                        '</div>');
        scrolling();
      };

      ws.onclose = function(e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function() {
          connect();
        }, 5000);
      };

      ws.onerror = function(err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        ws.close();
      };

      return ws;
    }

    ws = connect();

    var message_textarea = $('#message_textarea');
    message_textarea.focus();
    //message_textarea.on("keyup", function(e) {
    //    if (e.keyCode === 13) {  // enter, return
    //        $('#chat_message_form').submit();
    //    }
    //});

    $('#chat_message_form').on("submit", function(e) {
        e.preventDefault();
        var message = $('#message_textarea').val();
        var chat_uuid = $('#chat_uuid').val();
        ws.send(JSON.stringify({
            'chat_uuid': chat_uuid,
            'message': message
        }));
        $('#message_textarea').val("");
    });

    scrolling(scrolling_speed=0);
    //End of chats area
});