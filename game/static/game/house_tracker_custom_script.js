// ==UserScript==
// @name     house_tracker
// @version  2
// @grant    none
// ==/UserScript==

USERNAME = "Ludo";

function register_offer(){
  //instead, I can use document.querySelectorAll('[data-qa-id]');
 	//loop over it, testing e.g. "adview_title" == elt.dataset.qaId
  //it would leed to smaller code, more readable (but slower)

	path_article = document.getElementById('grid').firstChild;
  path_article_header = path_article.firstChild.children[2];
  title = path_article_header.firstChild.firstChild.firstChild.innerText;
  price = path_article_header.firstChild.firstChild.children[1].innerText;
  page_created = path_article_header.children[1].innerText;
  ref = null;

  let criterias = path_article.children[5].children[1].children[0].children;
  console.log(criterias);
  for (crit of criterias){
    if ('data-qa-id' in crit.attributes){
      if (crit.attributes['data-qa-id'].value == "criteria_item_custom_ref")
        ref = crit.children[1].children[1].innerText;
    }
  }

  console.log(title);
  console.log(price);
  console.log(page_created);
  console.log(ref);


  var xhr = new XMLHttpRequest();
  xhr.open("POST", "https://legit.engineer/scrap", true);
  xhr.setRequestHeader('Content-Type', 'application/json');

  xhr.onload = function () {
  	alert('Request sent, status code : '+xhr.status);
	};

  xhr.send(JSON.stringify({
      title: title,
    	price: price,
    	page_created: page_created,
    	user: USERNAME,
    	ref: ref,
    	url: document.URL,
    	url-img: document.querySelectorAll('[alt="image-galerie-0"]')[0].src
  }));

}

function create_button(){

  var button = document. createElement("button");
  button.innerHTML = "Save";
  parent = document.getElementById('grid').firstChild;
  parent.insertBefore(button, parent.children[6]);
  button.addEventListener ("click", register_offer);
}


if (document.domain == "www.leboncoin.fr"){
	setTimeout(create_button, 2000);

}
