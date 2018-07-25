$(function(){
    // https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_client_applications
    var ws = new WebSocket("ws://192.168.0.13:5000/ws");
    ws.onopen = function() {
        /* Send message to server */
    };
    ws.onmessage = function (event) { 
        /* Receiving JSON from server and Initialize parameters*/
        var msg = JSON.parse(event.data);
        $("#slider-vertical").slider('value',msg['volume'])
        $("#amount").val(msg['volume'])
        document.getElementById("currentAlarm").innerHTML = "<h3>Current Alarm: " + msg['alarm'] + "</h3>"
    };

    ws.onclose = function() { 
        ws.send("Client closing connection");
    };                

    /* send new alarm time */
    $("#setAlarm").click(function(){
        var alarmTime = $('#time').val();
        var data = JSON.stringify({type:"alarm", value: alarmTime});
        ws.send(data);
    });

    /* Send new alarm time */
    $("#clear-alarm").click(function(){
        var data = JSON.stringify({type:"clear"});
        ws.send(data);
    });    

    /* Volume Slider */
    $( "#slider-vertical" ).slider({
        orientation: "horizontal",
        range: "min",
        min: 0,
        max: 100,
        value: 60,
        slide: function( event, ui ) {
            $( "#amount" ).val( ui.value );
        }
    });
    $( "#amount" ).val( $( "#slider-vertical" ).slider( "value" ) );

    /* send new volume */
    $( "#slider-vertical" ).mouseup(function() {
        var volume = $('#amount').val();
        var data = JSON.stringify({type:"volume", value: volume});
        console.log(volume);
        ws.send(data);
    });
    $( "#offButton" ).mouseup(function() {
        var data = JSON.stringify({type:"off"});
        ws.send(data)
    })
});
