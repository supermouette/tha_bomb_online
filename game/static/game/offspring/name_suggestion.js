let proposition = localStorage.getItem("proposition");
let inputElt = document.getElementById("user_suggestion_input");
let inputBtn = document.getElementById("send_button");
let can_vote = true;

if (proposition) {
  inputElt.disabled = true;
  inputElt.value = proposition;
  inputBtn.disabled = true;
}
function validate_suggestion() {
  fetch("/offspring/suggestion/" + inputElt.value).then((response) => {
    if (response.status == 200) {
      localStorage.setItem("proposition", inputElt.value);
      window.location.reload();
    } else {
      alert("Ce nom à déjà été proposé");
    }
  });
}

function popularity_update(name) {
  if (!can_vote) {
    return;
  }
  fetch("/offspring/suggestion/" + name + "/upvote").then((response) => {
    response.json().then((data) => {
      let elt = document.getElementById("popularity-" + name);
      elt.innerHTML = data.new_popularity;
      can_vote = false;
      disable_upvotes();
      localStorage.setItem("last_upvote_date", new Date().toLocaleDateString());
    });
  });
}

function disable_upvotes() {
  let buttons = document.getElementsByClassName("popularity-button");
  for (let b of buttons) {
    b.classList.add("popularity-button-disabled");
  }
}

if (
  localStorage.getItem("last_upvote_date") == new Date().toLocaleDateString()
) {
  disable_upvotes();
  can_vote = false;
}
