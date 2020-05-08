let url_data = document.getElementById('url_data').innerHTML;
let url_bomb_img = document.getElementById('url_bomb_img').innerHTML;
let url_wire_img = document.getElementById('url_wire_img').innerHTML;
let url_hidden_img = document.getElementById('url_hidden_img').innerHTML;
let url_nothing_img = document.getElementById('url_nothing_img').innerHTML;
let player_hand = document.getElementById('player_hand');

let current_player = document.getElementById('current_player');
let other_players = document.getElementsByClassName('other_player')

url_img = {"n":url_nothing_img, "w": url_wire_img, "b": url_bomb_img}
alt_img = {"n":"nothing", "w": 'wire', "b": 'bomb'}

function make_claim(){
    console.log("making a claim...");
    // do as if claim was success
    current_player.classList.remove('should_claim');
    for (button of current_player.getElementsByTagName('button')){
                button.disabled = true;
    }
    url = window.location.href+'/claim/'
    url += document.getElementById('wire_nb').value + "/";
    url += document.getElementById('bomb_nb').value;
    fetch(url).then(data=>{
        if (data.status != 200){
            alert('claim was not successfull');

            // revert state
            current_player.classList.add('should_claim');
            for (button of current_player.getElementsByTagName('button')){
                button.disabled = false;
            }
        }
        else{
            console.log("... claim was successfull");
        }
    });
}

function discover_card(event){
    if (current_player.classList.contains('should_play')){
        var target = event.target || event.srcElement;
        // do as if it worked
        target.style.visibility = "hidden";
        current_player.classList.remove('should_play');
        // make request
        url = window.location.href+'/discover/'
        url +=  target.id.split('_')[1]+ "/";
        url += target.id.split('_')[0];
        fetch(url).then(data=>{
            if (data.status != 200){
                console.log("failure when discovering card")
                // revert
                target.style.visibility = "hidden";
                current_player.classList.add('should_play');
            }
        });
    }
}

function refresh(){
    console.log("refresh...");
    fetch(url_data)
    .then(data=>{return data.json()})
    .then(res=>{
        // **** update own cards ****
        console.log(res);
        // clear
        player_hand.innerHTML = "";
        //update
        for (card of res['own_cards']){
            var element = document.createElement('div');
            element.classList.add('card_placeholder');
            var img = document.createElement('img');
            img.alt = alt_img[card];
            img.src= url_img[card];
            element.appendChild(img);
            player_hand.appendChild(element);
        }


        // **** find out who's turn it is ****
        // clear classlist
        // ... for player
        if (current_player.classList.contains('should_claim'))
            current_player.classList.remove('should_claim');
        if (current_player.classList.contains('should_play'))
            current_player.classList.remove('should_play');
        // ... for others
        for (other of other_players){
            if (other.classList.contains('should_claim')){
                other.classList.remove('should_claim');
            }
            if (other.classList.contains('should_play')){
                other.classList.remove('should_play');
            }
        }
        // is there a claim to do ?
        let claim = false;
        if (res['own_claim'][0]==null){ // if current player should claim
            claim = true;
            current_player.classList.add('should_claim');
            for (button of current_player.getElementsByTagName('button')){
                button.disabled = false;
                document.getElementById('wire_nb').value = 0;
                document.getElementById('bomb_nb').value = 0;
            }
        }
        else{ // if current player have already claimed
            for (button of current_player.getElementsByTagName('button')){
                button.disabled = true;
                document.getElementById('wire_nb').value = res['own_claim'][0];
                document.getElementById('bomb_nb').value = res['own_claim'][1];
            }
        }

        for (other of other_players){
            id = other.id.split('_')[1];
            if (res['others'][id][1]==null){
                other.classList.add('should_claim');
                other.getElementsByClassName('claim')[0].innerHTML = "no claim yet";
                claim = true;
            }
            else{
                claim_wire = res['other'][id][1];
                claim_bomb = res['other'][id][2];
                if (claim_wire==0 && claim_bomb==0){
                    other.getElementsByClassName('claim')[0].innerHTML = "nothing";
                }
                else if (claim_bomb==0){
                    other.getElementsByClassName('claim')[0].innerHTML = claim_wire + "wire(s)";
                }
                else if (claim_wire==0){
                    other.getElementsByClassName('claim')[0].innerHTML = "bomb";
                }
                else {
                    other.getElementsByClassName('claim')[0].innerHTML = claim_wire + "wire(s) and the bomb";
                }
            }
        }
        if (!claim){
            if (res['next_player']=="-1"){
                current_player.classList.add('should_play');
            }
            else{
                document.getElementById('player_'+res['next_player']).classList.add('should_play');
            }
        }
        // **** update other cards ****
        nb_slots = 6 - res['turn'];
        for (other of other_players){
            id = other.id.split('_')[1];
            // check nb_slots
            slots = other.getElementsByClassName('card_placeholder_other_player');
            while (slots.length != nb_slots){
                slots[slots.length-1].remove()
            }
            // fill/remove placeholders as needed
            let binary_hand = res['others'][id][0];
            for (var i = 0; i < nb_slots; i++) {
                bit = binary_hand & 1;
                if (bit){
                    slots[i].children[0].style.visibility = "visible";
                }
                else{
                    slots[i].children[0].style.visibility = "hidden";
                }
                binary_hand >>= 1;
            }
        }

        // **** update discovered cards****
        document.getElementById('nb_nothing_discovered').innerHTML = res['discovered'][0];
        document.getElementById('nb_wire_discovered').innerHTML = res['discovered'][1];
        document.getElementById('nb_bomb_discovered').innerHTML = res['discovered'][2];

        let victory = document.getElementById('victory');
        if (res['state']== 'b'){
            victory.classList.add('blue_victory');
            victory.innerHTML = "Blues wins ! ";
            for (other of other_players){
                if (res['colors'][other.id.split[1]] == 'b')
                    other.children[0].classList.add('blue_victory')
                else
                    other.children[0].classList.add('red_victory');
            }
        }
        else if (res['state']== 'r'){
            victory.classList.add('red_victory');
            victory.innerHTML = "Reds wins ! ";
            for (other of other_players){
                if (res['colors'][other.id.split[1]] == 'b')
                    other.children[0].classList.add('blue_victory')
                else
                    other.children[0].classList.add('red_victory');
            }
        }
        else {
            setTimeout(check, 10000);
        }
    })
}

//document.getElementById('refresh_button').addEventListener("click", refresh);
document.getElementById('make_claim').addEventListener("click", make_claim);

for (card of document.getElementsByClassName('clickable_card')){
    card.addEventListener("click", discover_card);
}

refresh();