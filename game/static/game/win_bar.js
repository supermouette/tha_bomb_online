let url = "/blue_ratio";
fetch(url).then(data=>{
    data.text().then(body=>{
        blue_ratio = parseFloat(body)*100
        document.getElementById('blue_bar').style.width = blue_ratio+"%";
    });
});