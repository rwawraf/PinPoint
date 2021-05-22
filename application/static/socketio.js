let socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on("connect", async function () {
    var usr_name = await loadName();
    if (usr_name != "") {
        socket.emit("event", {
            message: usr_name + " just connected to the server!",
            connect: true,
        });
    }
    var form = $("form#msgForm").on("submit", async function (e) {
        e.preventDefault();

        // get input from message box
        let msg_input = document.getElementById("msg");
        let user_input = msg_input.value;
        let user_name = await loadName();
        let room_id = await loadRoom();

        // clear msg box value
        msg_input.value = "";

        // send message to other users
        socket.emit("event", {
            message: user_input,
            name: user_name,
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

socket.on("message response", function (msg) {
    addMessages(msg, true);
});

socket.on("notification", function(notification){
    displayNotification(notification);
});