var computer = player == "X" ? "O" : "X";

function MakeMove(sender, move) {
    if ($(sender).text().trim() == "" && $("#messages").text().trim() == "") {
        $(sender).html(player);
        $.post(create_move_url, {'move': move},
            function(data) {
                if(data[0] != '') {
                    $("#cell" + data[0]).html(computer);
                }

                if (data[1] == "Over") {
                    $("#messages").html("GAME OVER! It was a tie");
                }
                else if (data[1] == "X" || data[1] == "O") {
                    $("#messages").html("THE WINNER IS " + data[1]);
                }
            }
        )
    }
}
