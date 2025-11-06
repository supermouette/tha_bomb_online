let try_nb = 0;
let column_idx = 1;
let current_row =
  document.getElementById("name_guess_table").children[0].children[0];
let max_try = 5;
let word_size = current_row.children.length;
let gameStatus = "";
let resultCodes = [];
let gameover = document.getElementById("gameover");

function isLetter(str) {
  return str.length === 1 && (str.match(/[a-z]/i) || str == ".");
}

function getCurrentWord() {
  return Array.from(current_row.children).reduce(
    (acc, val) => acc + val.innerHTML,
    ""
  );
}

function getAllWords() {
  words = [];
  for (let i = 0; i <= try_nb; i++) {
    row = document.getElementById("name_guess_table").children[0].children[i];
    word = Array.from(row.children).reduce(
      (acc, val) => acc + val.innerHTML,
      ""
    );
    if (!word.endsWith(" ")) {
      words.push(word);
    }
  }
  return words;
}

function addLetter(l) {
  if (column_idx >= word_size) {
    return;
  }
  current_row.children[column_idx].innerHTML = l;
  column_idx += 1;
}

function removeLetter() {
  if (column_idx == 1) {
    return;
  }
  column_idx -= 1;
  element = current_row.children[column_idx];
  element.innerHTML = "";
}

async function submitWordRequest(word) {
  if (gameStatus != "") {
    return;
  }
  request = await fetch("/offspring/guess/" + word);
  if (request.status != 200) {
    throw new Error();
  }
  return await request.json();
}

function won() {
  gameover.innerText = "Bien joué ! ";
  gameStatus = "won";
  victoryFireWork();
}

function lost() {
  gameover.innerText = "Dommage.... ré-essaye demain";
  gameStatus = "lost";
}

function save() {
  savePoint = {};
  savePoint.lastPlay = new Date().toLocaleDateString();
  savePoint.tries = getAllWords();
  savePoint.resultCodes = resultCodes;
  savePoint.gameStatus = gameStatus;
  savePoint.isRealName = isRealName;
  localStorage.setItem("savePoint", JSON.stringify(savePoint));
}

async function load() {
  savePoint = JSON.parse(localStorage.getItem("savePoint"));
  if (savePoint === null) {
    return;
  }
  if (savePoint.lastPlay != new Date().toLocaleDateString()) {
    return;
  }
  resultCodes = savePoint.resultCodes;
  for (let i = 0; i < savePoint.tries.length; i++) {
    word = savePoint.tries[i];
    // first letter each line is already filled
    for (let j = 1; j < word.length; j++) {
      addLetter(word[j]);
    }
    await fillWord(resultCodes[i], false);
    console.log(word);
    try_nb += 1;
    column_idx = 1;
    current_row =
      document.getElementById("name_guess_table").children[0].children[try_nb];
  }
  if (savePoint.gameStatus != "") {
    gameStatus = savePoint.gameStatus;
    if (gameStatus == "won") {
      isRealName = savePoint.isRealName;
      won();
    } else if (gameStatus == "lost") {
      lost();
    }
  }
}

async function fillWord(resultCode, isDelay = true) {
  for (let i = 0; i < word_size; i++) {
    if (resultCode[i] == 2) {
      current_row.children[i].classList.add("correct");
    } else if (resultCode[i] == 1) {
      current_row.children[i].classList.add("wrong_place");
    }
    if (isDelay) {
      await new Promise((resolve) => setTimeout(resolve, 200));
    }
  }
}

async function submitWord() {
  if (column_idx != word_size) {
    return;
  }
  result = await submitWordRequest(getCurrentWord());
  resultCode = result.result;
  resultCodes.push(resultCode);
  await fillWord(resultCode);
  if (resultCode.split("").every((char) => char === "2")) {
    isRealName = result.isRealName;
    won();
  } else if (try_nb < max_try - 1) {
    try_nb += 1;
    column_idx = 1;
    current_row =
      document.getElementById("name_guess_table").children[0].children[try_nb];
  } else {
    lost();
  }
  save();
}

load();

addEventListener("keydown", async (event) => {
  const tag = document.activeElement.tagName.toLowerCase();
  if (
    tag === "input" ||
    tag === "textarea" ||
    document.activeElement.isContentEditable
  ) {
    return;
  }
  if (gameStatus != "") {
    return;
  }
  key = event.key.toUpperCase();
  if (isLetter(key)) {
    addLetter(key);
  } else if (key == "BACKSPACE") {
    removeLetter();
  } else if (key == "ENTER") {
    submitWord();
  }
});

function virtualKey(key) {
  if (gameStatus != "") {
    return;
  }
  if (isLetter(key)) {
    addLetter(key);
  } else if (key == "BACKSPACE") {
    removeLetter();
  } else if (key == "ENTER") {
    submitWord();
  }
}

function createFirework(x, y) {
  const firework = document.createElement("div");
  firework.className = "firework";
  firework.style.left = x + "px";
  firework.style.top = y + "px";

  const particleCount = 30;
  for (let i = 0; i < particleCount; i++) {
    const p = document.createElement("div");
    p.className = "particle";

    const angle = (Math.PI * 2 * i) / particleCount;
    const radius = 100 + Math.random() * 50;

    const xMove = Math.cos(angle) * radius + "px";
    const yMove = Math.sin(angle) * radius + "px";

    p.style.setProperty("--x", xMove);
    p.style.setProperty("--y", yMove);

    // Couleurs aléatoires
    p.style.background = `radial-gradient(circle, hsl(${
      Math.random() * 360
    }, 100%, 60%), transparent)`;

    firework.appendChild(p);
  }

  document.body.appendChild(firework);

  // Nettoyage après animation
  setTimeout(() => firework.remove(), 1200);
}

function victoryFireWork() {
  const duration = 10000; // 10 secondes
  const interval = 500; // toutes les 0.5s

  const timer = setInterval(() => {
    const x = Math.random() * window.innerWidth;
    const y = Math.random() * window.innerHeight * 0.8; // un peu au-dessus du bas
    createFirework(x, y);
  }, interval);

  setTimeout(() => clearInterval(timer), duration);
}
