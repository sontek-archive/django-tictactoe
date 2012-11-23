var socket = io.connect();


socket.on("message", function(obj){
    if (obj.message.type == "message") {
        var data = eval(obj.message.data);

        if (data[1] == game_id) {
            if (data[0] == "game_over") {
                    winner = data[2];
                    game_over = true;

                    if (data[2] == "") {
                        SetMessage("Its a tie!");
                    }
                    else {
                        SetMessage("The winner is: " + data[2]);
                    }
                }
            else if (data[0] == "opponent_moved") {
                $('#cell' + data[3]).html(data[2]);
                SwapUser();
            }
        }
    }
});

function MakeMove(sender, move) {
    if (player == current_player && game_over == false) {
        if ($(sender).text().trim() == "") {
            $(sender).html(player);
            SwapUser();

            $.post(create_url, {'move': move},
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

socket.emit("subscribe:" + user_id);

function SetMessage(message) {
    $("#messages").html("<div>" + message + "</div>");
    $("#messages").show();
}

