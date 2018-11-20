function connect() {

    function sendNotification(data, order_status_change){
        message = "Message from " + data.message_user_name + ": <br>" + data.message + "<div class='text-right'><a href='/live-chat/"+ data.chat_uuid + "/' class='btn btn-sm'>Go to chat</a>";
        if (order_status_change==true){
            toastr.options.timeOut = 0;
            toastr.options.extendedTimeOut = 0;
        }

        if (data.color_type == "info"){
            toastr.info(message);
        }else{
           toastr.success(message);
        }
    }

     var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
     var url = ws_scheme+ '://' + window.location.host +
        '/ws/general/';
      var ws_general = new WebSocket(url);
      ws_general.onopen = function() {
        // subscribe to some channels
        //ws_general.send(JSON.stringify({
        //    //.... some message the I must send when I connect ....
        //}));
      };

      ws_general.onmessage = function(e) {
        var data = JSON.parse(e.data);
        if (data.type == "new_chat_message_notification" && window.location.href.indexOf(data.chat_uuid) == -1){
            sendNotification(data, order_status_change=false);
        }else if(data.type == "order_status_change"){
            if (window.location.href.indexOf(data.chat_uuid) == -1 ){
                sendNotification(data, order_status_change=true);
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