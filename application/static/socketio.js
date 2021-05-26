let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on("connect", async function () {
    var usr_name = await loadName();
    if (usr_name != "") {
        socket.emit("event", {
            message: usr_name + " just connected to the server!",
            connect: true,
        });
    }
    var form = $("form#sendBtn").on("click", async function (e) {
        e.preventDefault();

        // get input from message box
        let msg_input = document.getElementById("msg");
        let user_input = msg_input.value;
        let user_name = await loadName();
        let picture = await loadPicture();
        let room_id = await loadRoom();

        // clear msg box value
        msg_input.value = "";

        // send message to other users
        socket.emit("event", {
            message: user_input,
            name: user_name,
            picture: picture,
            type: 1,
            room_id: room_id
        });
    });
});

socket.on("disconnect", async function (msg) {
    var usr_name = await loadName();
    socket.emit("event", {
        message: usr_name + " just left the server...",
    });
});

socket.on("notification", function(notification){
    displayNotification(notification);
});

socket.on("leave_room", function (){
    leaveRoom();
});

socket.on("enter_room", function (){
    enterRoom();
});

