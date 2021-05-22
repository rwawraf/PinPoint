function deleteRoom(room_id){
    fetch("/delete-room", {
        method: "POST",
        body: JSON.stringify({room_id: room_id}),
    }).then((_res) => {
        window.location.href = "/rooms";
    });
}

function deleteNote(note_id){
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({note_id: note_id}),
    }).then((_res) => {
        window.location.href = "/notes";
    });
}

function editNote(note_id){
    fetch("/edit_note/", {
        method: "POST",
        body: JSON.stringify({note_id: note_id}),
    }).then((_res) => {
        window.location.href = "/edit-note/" + note_id;
    });
}

function addUser(user_id){
    fetch("/add-user", {
        method: "POST",
        body: JSON.stringify({user_id: user_id}),
    }).then((_res) => {
        window.location.href = "/users";
    });
}

function acceptUser(relation_id){
    fetch("/accept-user", {
        method: "POST",
        body: JSON.stringify({relation_id: relation_id}),
    }).then((_res) => {
        window.location.href = "/friends";
    });
}

function declineUser(relation_id){
    fetch("/decline-user", {
        method: "POST",
        body: JSON.stringify({relation_id: relation_id}),
    }).then((_res) => {
        window.location.href = "/users";
    });
}

function blockUser(relation_id){
    fetch("/block-user", {
        method: "POST",
        body: JSON.stringify({relation_id: relation_id}),
    }).then((_res) => {
        window.location.href = "/friends";
    });
}

function menuFunction() {
    var x = document.getElementById("menu_id");
    if (x.className === "menu") {
        x.className += " responsive";
    } else {
        x.className = "menu";
    }
}

async function addMessages(msg, scroll) {
    if (typeof msg.name !== "undefined") {
        var date = dateNow();

        if (typeof msg.time !== "undefined") {
            var n = msg.time;
        } else {
            var n = date;
        }
        var global_name = await loadName();
        var content;

        if(msg.type == 1){
            if (global_name == msg.name) {
            content =
                '<div class="container darker">' +
                '<b style="color:#000" class="left">' +
                msg.name +
                "</b><p>" +
                msg.message +
                '</p><span class="time-left">' +
                n +
                "</span></div>";
            }else{
                content =
                    '<div class="container">' +
                    '<b style="color:#000" class="right">' +
                    msg.name +
                    "</b><p>" +
                    msg.message +
                    '</p><span class="time-right">' +
                    n +
                    "</span></div>";
            }
        }
        if(msg.type == 2){
            content =   '<div class="user_joined">' +
                        '<p>' + msg.name + ' dołączył do pokoju</p>' +
                        '</div>';
        }

        if(msg.type == 3){
            content =   '<div class="user_left">' +
                        '<p>' + msg.name + ' wyszedł z pokoju</p>' +
                        '</div>';
        }
        // update div
        var messageDiv = document.getElementById("messages");
        messageDiv.innerHTML += content;
    }

    if (scroll) {
        scrollSmoothToBottom("messages");
    }
}

async function loadName() {
    return await fetch("/user/get-name")
        .then(async function (response) {
            return await response.json();
        })
        .then(function (text) {
            return text["name"];
        });
}

async function loadUserId() {
    return await fetch("/user/get-user-id")
        .then(async function (response) {
            return await response.json();
        })
        .then(function (text) {
            return text["user_id"];
        });
}

async function loadRoom() {
    return await fetch("/room/get-id")
        .then(async function (response){
            return await response.json()
        })
        .then(function (text){
            return text["room_id"]
        })
}

async function loadMessages() {
    return await fetch("/get-messages")
        .then(async function (response) {
            return await response.json();
        })
        .then(function (text) {
            console.log(text);
            return text;
        });
}

$(function () {
    $(".msgs").css({ height: $(window).height() * 0.7 + "px" });

    $(window).bind("resize", function () {
        $(".msgs").css({ height: $(window).height() * 0.7 + "px" });
    });
});

function scrollSmoothToBottom(id) {
    var div = document.getElementById(id);
    $("#" + id).animate(
        {
            scrollTop: div.scrollHeight - div.clientHeight,
        },
        500
    );
}

function dateNow() {
    var date = new Date();
    var aaaa = date.getFullYear();
    var gg = date.getDate();
    var mm = date.getMonth() + 1;

    if (gg < 10) gg = "0" + gg;

    if (mm < 10) mm = "0" + mm;

    var cur_day = aaaa + "-" + mm + "-" + gg;

    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    if (hours < 10) hours = "0" + hours;

    if (minutes < 10) minutes = "0" + minutes;

    if (seconds < 10) seconds = "0" + seconds;

    return cur_day + " " + hours + ":" + minutes;
}

async function sendNotification(user_id){
    let sender_name = await loadName();
    let sender_id = await loadUserId();
    let room_id = await loadRoom();

    socket.emit("notification", {sender_id: sender_id, sender_name: sender_name, receiver_id: user_id, room_id: room_id});
}

async function displayNotification(notification){
    let user_id = await loadUserId();
    if(notification.receiver_id == user_id){
        let content =   "<div class='notification'><div class='notification-message'> Użytkownik <span class='username'>" + notification.sender_name + "</span> zaprasza cię do pokoju!</div><div class='notification-buttons'><a ><button class='btn btn-danger' onclick='discardNotification()'>Odrzuć</button></a><a href='/chatroom/" + notification.room_id + "/enter'><button class='btn btn-success'>Akceptuj</button></a></div></div>";
        $('.notification-container').append(content);
        $('.notification-container').toggleClass('notification-visible');
    }

    setTimeout(function (){
        let visible = $('.notification-container').hasClass('notification-visible');
        if(visible){
            $('.notification-container').toggleClass('notification-visible');
        }

        $('.notification-container').html("");
    }, 15000);
}

function discardNotification(){
    $('.notification-container').toggleClass('notification-visible');
    $('.notification-container').html("");
}





