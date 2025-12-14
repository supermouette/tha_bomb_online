async function vote_name_guess() {
  let top1 = document.getElementById("top_1").value;
  let top2 = document.getElementById("top_2").value;
  let top3 = document.getElementById("top_3").value;

  let set = new Set([top1, top2, top3]);
  if (set.size != 3) {
    alert("Vous devez voter pour des noms différents");
    return;
  }

  request = await fetch(`/offspring/guess_vote/${top1}/${top2}/${top3}`);
  if (request.status != 200) {
    alert("vote invalide");
    throw new Error();
  }
  localStorage.setItem("guess_name_already_voted", `${top1}/${top2}/${top3}`);
  document.location.reload();
  return;
}

already_voted = localStorage.getItem("guess_name_already_voted");

if (already_voted) {
  document.getElementById("send_top_button").disabled = true;
  let top1 = document.getElementById("top_1");
  let top2 = document.getElementById("top_2");
  let top3 = document.getElementById("top_3");
  top1.disabled = true;
  top2.disabled = true;
  top3.disabled = true;
  let names = already_voted.split("/");
  top1.value = names[0];
  top2.value = names[1];
  top3.value = names[2];
}
