const room = document.querySelector("#room_name").innerHTML;
const main = document.getElementsByTagName("main")[0];
const clickElt = document.querySelector("#click");
const totalElt = document.querySelector("#total");
const playersElt = document.querySelector("#active_player");
const contribution = document.querySelector("#contribution_nb");
const notif = document.querySelector("#notif_container");
const next_reward = document.querySelector("#next_reward");
const rewards_count = document.querySelector("#rewards_count");
const overlay_container = document.querySelector("#overlay-svg");
const uuid = crypto.randomUUID();
var clickCounter = 0;

const socket = new WebSocket(
  "ws://" + window.location.host + "/ws/clicker/" + room + "/"
);

socket.onmessage = function (e) {
  const data = JSON.parse(e.data);

  if (["clicker_player_up", "clicker_player_down"].includes(data.type)) {
    playersElt.innerHTML = data.total;
  } else if (data.type == "clicker_total_up") {
    totalElt.innerHTML = data.total;
    const newDiv = document.createElement("div");
    newDiv.innerHTML = "+" + data.click_power;
    newDiv.id = "up-" + data.total;
    if (data.options.uuid == uuid) {
      newDiv.classList.add("up");
      clickCounter += data.click_power;
    } else {
      newDiv.classList.add("up_others");
    }
    const maxTop = main.offsetHeight - 50;
    const maxLeft = main.offsetWidth - 50;
    newDiv.style.top = data.options.coords[0] * maxTop + "px";
    newDiv.style.left = data.options.coords[1] * maxLeft + "px";
    main.appendChild(newDiv);
    contribution.innerHTML = `${clickCounter} (${parseInt(
      (100 * clickCounter) / totalElt.innerHTML,
      10
    )}%)`;
    anime({
      targets: "#" + newDiv.id,
      autoplay: true,
      duration: 6000,
      opacity: 0,
      translateY: -100,
      complete: function (anime) {
        anime.animatables[0].target.remove();
      },
    });

    let old_rewards_count = rewards_count.innerHTML;
    while (rewards_count.innerHTML != data.active_rewards.length) {
      const newDiv = document.createElement("div");
      newDiv.innerHTML = data.active_rewards[rewards_count.innerHTML];
      newDiv.classList.add("notif");
      document.querySelector("#notif_container").appendChild(newDiv);
      rewards_count.innerHTML = parseInt(rewards_count.innerHTML) + 1;
    }
    if (next_reward.innerHTML != data.next_reward) {
      rewards(old_rewards_count, data.active_rewards.length);
      next_reward.innerHTML = data.next_reward;
      animate_notif();
    }
  }
};

socket.onclose = function (e) {
  console.error("socket closed unexpectedly");
};

socket.onopen = function () {
  document.querySelector("#click").onclick = function (e) {
    const maxTop = main.offsetHeight - 50;
    const maxLeft = main.offsetWidth - 50;
    coords = [
      (clickElt.offsetTop + 25) / maxTop,
      (clickElt.offsetLeft + 25 + 5 - 10 * Math.random()) / maxLeft,
    ];
    contrib = parseInt((100 * clickCounter) / totalElt.innerHTML, 10);
    socket.send(JSON.stringify({ uuid, coords, contrib }));
  };
  animate_notif();
};

function animate_btn() {
  const maxTop = main.offsetHeight - 50;
  const maxLeft = main.offsetWidth - 50;
  anime({
    targets: "#click",
    top: function () {
      return anime.random(0, maxTop);
    },
    left: function () {
      return anime.random(0, maxLeft);
    },
    easing: "linear",
    duration: 10000,
    complete: animate_btn,
  });
}

function animate_notif() {
  if (document.querySelector("#notif_container").children.length > 0) {
    anime({
      targets: "#notif_container > .notif:first-child",
      opacity: 0,
      easing: "easeInCubic",
      duration: 1000,
      delay: 5000,
      complete: () => {
        document
          .querySelector("#notif_container > .notif:first-child")
          ?.remove();
        animate_notif();
      },
    });
  }
}

var color = { hue: 0 };
var color_anime = anime({
  targets: color,
  hue: 360,
  duration: 10000,
  loop: true,
  easing: "linear",
  autoplay: false,
  update: function () {
    main.style.backgroundColor = `hsl(${color.hue} 100% 33.3%)`;
  },
});

function rewards(old_count, new_count) {
  if (old_count == 0 && new_count >= 1) {
    animate_btn();
  }
  if (old_count <= 2 && new_count == 3) {
    color_anime.play();
  }
  if (old_count <= 3 && new_count >= 4) {
    color_anime.pause();
    main.style.backgroundColor = 'hsl(180 100% 33.3%)';
  }
  if (old_count <= 4 && new_count >= 5) {
    overlay_container.style.display = "block";
  }
  if (old_count <= 6 && new_count >= 7) {
    overlay_container.style.display = "none";
  }
}

rewards(0, rewards_count.innerHTML);

const overlay = document.querySelector("#overlay");
const circle = document.querySelector("#overlay-circle");


document.addEventListener('mousemove', function(event) {
    const mouseX = event.clientX;
    const mouseY = event.clientY;

    circle.setAttribute('cx', mouseX);
    circle.setAttribute('cy', mouseY-50);    
  });