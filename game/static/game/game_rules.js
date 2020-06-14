let en_div = document.getElementById('english_rules');
let fr_div = document.getElementById('french_rules');

function toggle_en(){
    fr_div.hidden = true;
    en_div.hidden = false;
}

function toggle_fr(){
    fr_div.hidden = false;
    en_div.hidden = true;
}

document.getElementById('chose_en').addEventListener("click", toggle_en);
document.getElementById('chose_fr').addEventListener("click", toggle_fr);