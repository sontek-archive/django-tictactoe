var computer = player == "X" ? "O" : "X";

function MakeMove(sender, move) {
    if (player == current_player && winner == "None") {
        if ($(sender).text().trim() == "") {
            $(sender).html(player);
            SwapUser();

            $.post(create_move_url, {'move': move},
                function(data) {
                    SwapUser();

                    if(data[0] != '') {
                        $("#cell" + data[0]).html(computer);
                    }

                    if (data[1] == "Over") {
                        SetMessage("GAME OVER! It was a tie");
                    }
                    else if (data[1] == "X" || data[1] == "O") {
                        winner = data[1];
                        SetMessage("THE WINNER IS " + data[1]);
                    }

                }
            )
        }
    }
}

function play_move(obj)
{
    if (obj.message.type == "message") {
        var channel = obj.message.channel.replace("#", "");
        if (channel == game_id) {
            var data = eval(obj.message.data);
            if (data[0] != player) {
                $("#cell" + data[1]).html(data[0]);
                if (data.length == 2) {
                    current_player = player;
                    SetMessage("Your turn!");
                }
                else {
                    if (data[2] == "X" || data[2] == "O") {
                        SetMessage("Game Over, winner is " + data[2]);
                    }
                    else {
                        SetMessage("Game Over, its a tie");
                    }
                }
            }
            else {
                current_player = computer;
                SetMessage("Your opponents turn!");
            }
        }
    }
}

if (playing_computer == "False") {
    socket.connect();

    socket.on('message', function(obj){
        play_move(obj);
    });

    socket.send("subscribe:#" + game_id);
}

function SetMessage(message) {
    $("#messages").html(message);
    $("#playagain").show();
}

function SwapUser() {
    if (current_player == player) {
        current_player = computer;
    } else {
        current_player = player;
    }
}
