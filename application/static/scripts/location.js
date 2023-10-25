let $input;
let $sugList;
let $div;
let $suggestions

$(document).ready(function () {
    $input = $('#location-input');
    $sugList = $('#sug-list');
    $div = $('#location-div');
    $input.on('keyup', searchHandler);
});

async function search(term){
    if (term.length >= 2){
        let url = `/api/locations/${term}`;
        let resp = await axios.get(url);
        return resp.data;
    }
    return;
}

async function searchHandler(e) {
	res = await search($input.val());
    console.log(res)
	showSuggestions(res);
}

function showSuggestions(results) {
	$sugList.html('');
	for (let result of results){
		$li = $(`<li class='suggestion'>${result}</li>`);
		$sugList.append($li);
	}
    $suggestions = $('.suggestion');
    $suggestions.on('click', useSuggestion)
}

function useSuggestion(e) {
	$input.val(e.target.innerText);
	showSuggestions([]);
}