let url_init_game = document.getElementById('url_init_game').innerHTML;
let url_isinit = document.getElementById('url_isinit').innerHTML;

function init(){
    fetch(url_init_game)
    .then(data=>{
        if (data.status != 200){
            alert('There was an error');
        }
        else{
            document.location.reload(true);
        }
    })
}

document.getElementById('link_to_init').addEventListener("click", init);


function is_init(){
    fetch(url_isinit)
    .then(data=>{ return data.text()})
    .then(data=>{ if (data != '0'){
        document.location.reload(true);
        }
    })
}