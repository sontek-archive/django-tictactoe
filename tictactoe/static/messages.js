if ($("#messages").text().trim() == "") {
    $("#messages").hide();
}

if ($("#notifications").text().trim() == "") {
    $("#notifications").hide();
}

socket = io.connect();

socket.on("message", function(obj){
    if (obj.message.type == "message") {
        var data = eval(obj.message.data);

        if (data[0] == "new_invite") {
            SetNotificationMessage("You have a new game invite from " + data[1] + "<a href='" + data[2] + "'>Accept?</a>");
        }
        else if (data[0] == "game_started") {
            SetNotificationMessage("A new game has started <a href='/games/" + data[1] + "/'>here</a>");
        }
        else if (data[0] == "game_over") {
            if (data[1] == game_id) {
                winner = data[2];
                game_over = true;

                if (data[2] == "") {
                    SetMessage("Its a tie!");
                }
                else {
                    SetMessage("The winner is: " + data[2]);
                }
            }
            else {
                SetMessage("A game has finished <a href='/games/" + data[1] + "/'>here</a>");
            }
        }
        else if (data[0] == "opponent_moved") {
            if (data[1] == game_id) {
                $('#cell' + data[3]).html(data[2]);
                SwapUser();
            }
            else {
                SetMessage("Your opponent has played <a href='/games/" + game_id + "/'>here</a>");
            }
        }
    }
});

function MakeMove(sender, move) {
    if (player == current_player && game_over == false) {
        if ($(sender).text().trim() == "") {
            $(sender).html(player);
            SwapUser();

            $.post(create_move_url, {'move': move},
                function(data) {
                    // successfully made a move
                }
            )
        }
    }
}

function SwapUser() {
    var computer = player == "X" ? "O" : "X";

    if (current_player == player) {
        current_player = computer;
        SetMessage("Your opponents turn!");
    } else {
        current_player = player;
        SetMessage("Your turn!");
    }
}

socket.send("subscribe:" + user_id);

function SetNotificationMessage(message) {
    $("#notifications").html("<div>" + message + "</div>");
    $("#notifications").show();
}

function SetMessage(message) {
    $("#messages").html("<div>" + message + "</div>");
    $("#messages").show();
}
