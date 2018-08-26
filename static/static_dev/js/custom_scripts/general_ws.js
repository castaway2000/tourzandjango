function connect() {

    function sendNotification(data){
        message = "Message from " + data.message_user_name + ": <br>" + data.message + "<div class='text-right'><a href='/live-chat/"+ data.chat_uuid + "/' class='btn btn-sm'>Go to chat</a>";
        toastr.options.timeOut = 0;
        toastr.options.extendedTimeOut = 0;

        if (data.color_type == "info"){
            toastr.info(message);
        }else{
           toastr.success(message);
        }
    }

    console.log("connecting");
     var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
     var url = ws_scheme+ '://' + window.location.host +
        '/ws/general/';

      var ws_general = new WebSocket(url);
       console.log(ws_general);
      ws_general.onopen = function() {
        // subscribe to some channels
        //ws_general.send(JSON.stringify({
        //    //.... some message the I must send when I connect ....
        //}));
      };

      ws_general.onmessage = function(e) {
          console.log("message in general");
        var data = JSON.parse(e.data);
          console.log(data);
        if (data.type == "new_chat_message_notification" && window.location.href.indexOf(data.chat_uuid) == -1){
            sendNotification(data);
        }else if(data.type == "order_status_change"){
            if (window.location.href.indexOf(data.chat_uuid) == -1 ){
                sendNotification(data);
            }else{
                window.location.reload();
            }
        }
      };

      ws_general.onclose = function(e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function() {
          connect();
        }, 5000);
      };

      ws_general.onerror = function(err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket');
        ws_general.close();
      };

      return ws_general;
}

ws_general = connect();