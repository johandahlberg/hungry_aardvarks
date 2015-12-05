
function scrollTo(id) {
	$('html,body').animate({
		scrollTop : $("#" + id).offset().top
	}, 'slow');
}

// On click post url...
$( "#annotate-btn" ).click(function() {
  annotate();
});

function annotate_success(response) {
    console.log(response.keywords);
    $(response.keywords).each(function(index) {
        console.log(response.keywords[index]);
        var text = response.keywords[index].text;
        var relevance = response.keywords[index].relevance;
        $("#annotation-list").append(
            '<li class="list-group-item"><span class="badge">' + this.relevance + '</span>' + this.text + '</li>');
    });
    console.log(response.message);
    scrollTo("annotations");
}

function annotate() {
    var input = document.getElementById('url').value;
    console.log("input is: " + input);

    var url = "http://localhost:8888/insight"
    var data = '{ "url": "' + input + '" }'

    $.ajax({
        type: "POST",
        url: url,
        data: data,
        success: annotate_success,
        dataType: "json"
    });
}