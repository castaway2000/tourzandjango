function connect() {
    console.log("connecting");
     var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
     var url = ws_scheme+ '://' + window.location.host +
        '/ws/general/';

      var ws = new WebSocket(url);
       console.log(ws);
      ws.onopen = function() {
        // subscribe to some channels
        //ws.send(JSON.stringify({
        //    //.... some message the I must send when I connect ....
        //}));
      };

      ws.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data.type == "new_chat_message_notification" && window.location.href.indexOf(data.chat_uuid) == -1 ){
            message = "Message from " + data.message_user_name + ": <br>" + data.message + "<div class='text-right'><a href='/live-chat/"+ data.chat_uuid + "/' class='btn btn-sm'>Go to chat</a>";
            toastr.options.timeOut = 0;
            toastr.options.extendedTimeOut = 0;
            toastr.success(message);
        }
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