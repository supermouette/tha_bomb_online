// ==UserScript==
// @name     house_tracker
// @version  1
// @grant    none
// ==/UserScript==

USERNAME = "ludovic"

function register_offer(){
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
  xhr.send(JSON.stringify({
      title: title,
    	price: price,
    	page_created: page_created,
    	user: USERNAME,
    	ref: ref,
    	url: document.URL,
  }));
  alert('saved succesfully');

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
