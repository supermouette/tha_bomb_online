let countdown_elt = document.getElementById("countdown");
let countdown_parent = document.getElementById("countdown_parent");

let release_date = new Date("2026-01-15T00:00:01+01:00");

function updateCountdown() {
  const now = new Date(
    new Date().toLocaleString("en-US", { timeZone: "Europe/Paris" })
  );

  distance = release_date - now;
  if (distance < 0) {
    countdown_parent.innerText = "C'est l'heure de découvrir le vrai prénom !";
    return;
  }

  const days = Math.floor(distance / (1000 * 60 * 60 * 24));
  const hours = Math.floor(
    (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
  );
  const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((distance % (1000 * 60)) / 1000);
  const hh = String(hours).padStart(2, "0");
  const mm = String(minutes).padStart(2, "0");
  const ss = String(seconds).padStart(2, "0");

  countdown_elt.innerText = `${days}:${hh}:${mm}:${ss}`;
}

updateCountdown();
const timer = setInterval(function () {
  updateCountdown();
}, 1000);
