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
        let url = `/api/addresses/${term}`;
        let resp = await axios.get(url);
        return resp.data;
    }
    return;
}

async function searchHandler(e) {
	res = await search($input.val());
	showSuggestions(res);
}

function showSuggestions(results) {
	$sugList.html('');
    if (results.length === 0){
        $li = $(`<li class='suggestion'>Sorry no results found :(</li>`);
		$sugList.append($li);
    }
    else{
        for (let result of results){
            $li = $(`<li class='suggestion'>${result}</li>`);
            $sugList.append($li);
        }
        $suggestions = $('.suggestion');
        $suggestions.on('click', useSuggestion)
    }
}

function useSuggestion(e) {
	$input.val(e.target.innerText);
	$sugList.html('');
}