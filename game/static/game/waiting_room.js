let url_wr = document.getElementById('url_room_list').innerHTML;
let tbody = document.getElementsByTagName('tbody')[0];

function refresh(){
    fetch(url_wr)
    .then(data=>{return data.json()})
    .then(res=>{
        let content = ""
        res.forEach(function (item, index) {
            content += '<tr><td>'+item[0]+'</td><td>'+item[1]+'</td><td><a href="'+item[2]+'">join</a></td></tr>'
        });
        tbody.innerHTML = content;
        setTimeout(refresh, 5000);
    })
}

document.getElementById('refresh_button').addEventListener("click", refresh);
refresh();