let url = document.getElementById('url_room_list').innerHTML;
let tbody = document.getElementsByTagName('tbody')[0];

function refresh(){
    fetch(url)
    .then(data=>{return data.json()})
    .then(res=>{
        // clear tbody
        //tbody.innerHTML = "";
        console.log(res)
        let content = ""
        res.forEach(function (item, index) {
            content += '<tr><td>'+item[0]+'</td><td>'+item[1]+'</td><td><a href="'+item[2]+'">join</a></td></tr>'
        });
        console.log(content);
        tbody.innerHTML = content;
        setTimeout(refresh, 5000);
    })
}

document.getElementById('refresh_button').addEventListener("click", refresh);
refresh();