let betHash = localStorage.getItem("betHash");

if (betHash) {
  let betName = localStorage.getItem("betName");
  let betDate = localStorage.getItem("betDate");
  document.getElementById("input-bet-name").value = betName;
  document.getElementById("input-bet-date").value = betDate;
  document.getElementById("input-bet-name").disabled = true;
  document.getElementById("input-bet-date").disabled = true;
  document.getElementById("input-bet-button").disabled = true;
}

fetch("/offspring/get_bet/" + betHash).then((response) => {
  response.json().then((data) => {
    let histogram = data.histogram;
    let max_value = histogram.reduce(
      (acc, cur) => (acc > cur.count ? acc : cur.count),
      0
    );
    for (bin of histogram) {
      let color = 255 - 255 * (bin.count / max_value);
      let elt = document.getElementById(bin.date_bucket);
      elt.style.backgroundColor = `rgb(${color}, 255, ${color})`;
      elt.title = bin.count;
    }
    if (data.user_bet_id) {
      let color = 255 - 255 * (bin.count / max_value);
      let elt = document.getElementById(bin.date_bucket);
      elt.style.backgroundColor = `rgb(255, ${color}, ${color})`;
    }
  });
});

async function placeBet() {
  let name = document.getElementById("input-bet-name").value;
  let date_bet = document.getElementById("input-bet-date").value;
  if (date_bet == "") {
    alert("vérifiez que la date et l'heure soient correctement remplies");
    return;
  }
  let name_hash = await hashString(name);
  await fetch("/offspring/place_bet", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, date_bet, name_hash }),
  });
  localStorage.setItem("betHash", name_hash);
  localStorage.setItem("betName", name);
  localStorage.setItem("betDate", date_bet);
  document.location.reload();
}

async function hashString(inputString) {
  const encoder = new TextEncoder();
  const data = encoder.encode(inputString);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);

  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");

  return hashHex;
}
