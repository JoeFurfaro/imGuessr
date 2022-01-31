//let socket = new WebSocket("ws://localhost:5678");
let socket = new WebSocket("wss://svcrafted.com:5678");

socket.onopen = (event) => {
    $("#name-select").show();
    $("#choose-name").addClass('choose-name-animation');
    $("#choose-name-sub").addClass('choose-name-sub-animation');
    $("#name-select-field").addClass('name-select-animation');
    $(".name-img").addClass('name-img-animated');
}

socket.onclose = (event) => {
    console.log("Closed socket!")
    alert("Lost connection! Try refreshing the page.");
}

socket.onmessage = (event) => {
    let data = JSON.parse(event.data);
    console.log(data);
    if(data.status == "JOIN_FAILED") {
        $("#name-chars").css("color", "#FF0000");
        $("#name-chars").html("That name is taken!")
    } else if(data.status == "JOIN_SUCCESS") {
        $("#name-select").fadeOut(300, ()=> {
            $("#choose-name").removeClass('choose-name-animation');
            $("#choose-name-sub").removeClass('choose-name-sub-animation');
            $("#name-select-field").removeClass('name-select-animation');
            $(".name-img").removeClass('name-img-animated');
            $("#chatbox").fadeIn(300);
            $("#leaderboard-box").fadeIn(300);
        });
    } else if(data.status == "MESSAGE" || data.status == "GUESS") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post"><span class="chat-name">' + data.player + '&nbsp;</span>' + data.data + '</p>';
        $("#chat").html(curChat + newChat);
        chatScrollBottom();
    } else if(data.status == "POST_ROUND") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post"><span class="chat-name">There is a game in progress and a round just finished. A new round will start soon!</span></p>';
        $("#chat").html(curChat + newChat);
        chatScrollBottom();
    } else if(data.status == "STARTING_SOON") {
        if(data.starting_in % 10 == 0 || data.starting_in <= 10) {
            let curChat = $("#chat").html();
            let newChat = '<p class="chat-post soon">The game is starting in ' + data.starting_in + ' second(s)!</p>';
            $("#chat").html(curChat + newChat);
            $("#seconds").html('second(s) until game start');
            chatScrollBottom();
        }
        $("#start-countdown").html(data.starting_in);
        if($("#game").is(":visible")) {
            $("#game").fadeOut(500, () => {
                if(!$("#pregame").is(":visible")) {
                    $("#pregame").fadeIn(300);
                }
            });
        } else {
            if(!$("#pregame").is(":visible")) {
                $("#pregame").fadeIn(300);
            }
        }
    } else if(data.status == "STARTING") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post now">The game has begun!</p>';
        $("#chat").html(curChat + newChat);
        $("#image-panel").hide();
        $("#postround").hide();
        chatScrollBottom();
        $("#pregame").fadeOut(500, () => {
            $("#game").fadeIn(200);
        });
        $("#pr-2b").html("");
        $("#pr-2c").html("");
    } else if(data.status == "PLAYER_LIST") {
        $("#players").html("");
        for(let name of data.players) {
            let cur = $("#players").html();
            let newP = '<p class="text blue player">' + name + '</p>';
            $("#players").html(cur + newP);
        }
    } else if(data.status == "STARTING_ROUND") {
        $("#display-image").attr("src", "");
    } else if(data.status == "NEW_ROUND") {
        $("#postround").fadeOut(200, () => {
            $("#image-panel").delay(0).fadeIn(200);  
            $("#pr-1").removeClass('pr-1-animate');
            $("#pr-2").removeClass('pr-2-animate');
            $("#pr-2b").removeClass('pr-2-animate');
            $("#pr-2c").removeClass('pr-2-animate');
            $("#pr-3").removeClass('pr-3-animate');
        });
        $("#display-image").attr("src", data.img_url + "?" + new Date().getTime());
        console.log($("#display-image").attr("width"));
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post"><span class="chat-name">A new round has started. Guess what you think the image is in the lobby chat!</span></p>';
        $("#chat").html(curChat + newChat);
        chatScrollBottom();
    }else if(data.status == "ROUND_PASSED") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post passed"><span class="chat-name-passed">' + data.player + '</span> won the round by guessing <span class="chat-name-passed">' + data.data + '</span>. Total rounds passed: <span class="chat-name-passed">' + data.new_score + '</span></p>';
        $("#chat").html(curChat + newChat);
        $("#pr-1").html("Answer: " + data.data);
        $("#pr-1").css("color", "#3b5e3c");
        $("#pr-2").html(data.player + " scored the point!");
        $("#pr-2").css("color", "#4ae04d");
        $("#pr-3").html("Total rounds passed: " + data.new_score);
        $("#image-panel").fadeOut(200, () => {
            $("#postround").fadeIn(80);
            $("#pr-1").addClass('pr-1-animate');
            $("#pr-2").addClass('pr-2-animate');
            $("#pr-3").addClass('pr-3-animate');
        });
        updateLeaderboard(data.scores);
        chatScrollBottom();
    } else if(data.status == "ROUND_FAILED") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post failed">The correct answer was <span class="chat-name-failed">' + data.word + '</span>. Total lives remaining: <span class="chat-name-failed">' + data.lives + '</span></p>';
        $("#chat").html(curChat + newChat);
        $("#pr-1").html("Answer: " + data.word);
        $("#pr-1").css("color", "#9e2d2b");
        $("#pr-2").html("Nobody guessed the correct answer.");
        $("#pr-2").css("color", "#fc5956");
        $("#pr-3").html("Lives remaining: " + data.lives);
        $("#image-panel").fadeOut(200, () => {
            $("#postround").fadeIn(80);
            $("#pr-1").addClass('pr-1-animate');
            $("#pr-2").addClass('pr-2-animate');
            $("#pr-2b").addClass('pr-2-animate');
            $("#pr-2c").addClass('pr-2-animate');
            $("#pr-3").addClass('pr-3-animate');
        });
        chatScrollBottom();
    } else if(data.status == "ROUND_TIME_LEFT") {
        if(data.time_left % 15 == 0 || data.time_left <= 10) {
            let curChat = $("#chat").html();
            let newChat = '<p class="chat-post text-secondary">' + data.time_left + ' second(s) left in the round.</p>';
            $("#chat").html(curChat + newChat);
            chatScrollBottom();
        }
        $("#start-countdown").html(data.starting_in);
    } else if(data.status == "GAME_OVER") {
        let curChat = $("#chat").html();
        let newChat = '<p class="chat-post failed"><span class="chat-name-failed">GAME OVER</span>. There are no lives left!</span></p>';
        $("#chat").html(curChat + newChat);
        $("#pr-1").html("Game Over");
        $("#pr-1").css("color", "#9e2d2b");
        $("#pr-2").css("color", "#b58304");
        let i = 1;
        let hasWinners = false;
        for(let item of data.scores) {
            hasWinners = true;
            if(i == 1)
                $("#pr-2").html("&#129351;&nbsp;" + item.player + "&nbsp;(" + item.score + ")");
            else if(i == 2)
                $("#pr-2b").html("&#129352;&nbsp;" + item.player + "&nbsp;(" + item.score + ")");
            else if(i == 3)
                $("#pr-2c").html("&#129353;&nbsp;" + item.player + "&nbsp;(" + item.score + ")");
            if(i > 3)
                break;
            i++;
        }
        if(!hasWinners) {
            $("#pr-2").css("color", "#444444");
            $("#pr-2").html("There were no winners.");
        }
        $("#pr-3").html("A new lobby will start shortly!");
        if($("#image-panel").is(":visible")) {
            $("#image-panel").fadeOut(200, () => {
                $("#postround").fadeIn(80);
                $("#pr-1").addClass('pr-1-animate');
                $("#pr-2").addClass('pr-2-animate');
                $("#pr-3").addClass('pr-3-animate');
            });
        } else {
            $("#postround").fadeIn(80);
            $("#pr-1").addClass('pr-1-animate');
            $("#pr-2").addClass('pr-2-animate');
            $("#pr-3").addClass('pr-3-animate');
        }
        
        chatScrollBottom();
    } else if(data.status == "STARTING_GAME") {
        $("#chat").html("");
        $("#leaderboard").html('<p class="text ml-auto mr-auto" style="width:90%">Players that have scored points will appear here, ranked in order of their score.</p>');
    } else if(data.status == "IN_GAME") {
        $("#pregame").hide();
        $("#game").fadeIn(300);
        updateLeaderboard(data.scores);
    } else if(data.status == "HINT") {
        let curChat = $("#chat").html();
        let newChat = '<p class="hint-post chat-post" style="font-weight:bold">HINT: <span class="hint">' + data.data + '</span></p>';
        $("#chat").html(curChat + newChat);
        chatScrollBottom();
    }
}

function updateLeaderboard(scores) {
    console.log("updating");
    $("#leaderboard").html("");
    let html = "";
    let emoji = "";
    let i = 1;
    for(let item of scores) {
        if(i == 1)
            html += '<p class="text lb-gold ml-auto mr-auto " style="width:90%">[#' + i + '] &#129351;&nbsp;' + item.player + ' - &nbsp;' + item.score + '</p>';
        else if(i == 2)
            html += '<p class="text lb-silver ml-auto mr-auto" style="width:90%">[#' + i + '] &#129352;&nbsp;' + item.player + ' - &nbsp;' + item.score + '</p>';
        else if(i == 3)
            html += '<p class="text lb-bronze ml-auto mr-auto" style="width:90%">[#' + i + '] &#129353;&nbsp;' + item.player + ' - &nbsp;' + item.score + '</p>';
        else
            html += '<p class="text lb-reg ml-auto mr-auto" style="width:90%">[#' + i + '] ' + item.player + ' - &nbsp;' + item.score + '</p>';
        i++;
    }
    if(html == "") {
        html = '<p class="text ml-auto mr-auto" style="width:90%">Players that have scored points will appear here, ranked by their score.</p>';
    }
    $("#leaderboard").html(html);
}

function chatScrollBottom() {
    var objDiv = document.getElementById("chat");
    objDiv.scrollTop = objDiv.scrollHeight;
}

function nameKeyPress(event) {
    let name = $("#name-select-field").val();
    if(event.keyCode == 13 && name.length <= 15 && name !== "") {
        socket.send(name);
    }
    if(name == "") {
        $("#name-chars").hide();
    } else {
        $("#name-chars").show();
        $("#name-chars").html(name.length + "/15");
        if(name.length > 15)
            $("#name-chars").css("color", "#FF0000");
        else
            $("#name-chars").css("color", "#000000");
    }
}

function chatKeyPress(event) {
    let msg = $("#send-chat-field").val();
    if(event.keyCode == 13 && msg !== "") {
        socket.send(msg);
        $("#send-chat-field").val("");
    }
}

function guess(event) {
    let msg = $("#guess-field").val();
    if(event.keyCode == 13 && msg !== "") {
        socket.send(msg);
        $("#guess-field").val("");
    }
}
