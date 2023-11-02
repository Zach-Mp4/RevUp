$button = $('#rsvp');
let meetId = $button.data('meetid');
$(document).ready(function () {
    $button = $('#rsvp');
    meetId = $button.data('meetid');
    $button.on('click', clickHandler);
});

function changeColor(resp){
    if (resp['data']['action'] === 'rsvpd'){
        $button.addClass('btn-success');
        $button.removeClass('btn-danger');
    }
    else{
        $button.addClass('btn-danger');
        $button.removeClass('btn-success');
    }
}

async function clickHandler(){
    const url = `/api/rsvp/${meetId}`;
    let cars = await axios.get('/api/cars/get_cars');
    console.log(cars);
    if (cars.data === 'None' || $button.hasClass('btn-success')){
        let resp = await axios.post(url);
        changeColor(resp);
        return;
    }
    cars = cars.data;
    $('#rsvp-div').append('<ul id="cars-list"></ul>');
    for (let car of cars){
        $('#cars-list').append(`<li class="car-select" id="${car.id}">${car.year} ${car.make} ${car.model}</li>`);
    }
    $('.car-select').on('click', carClickHandler);
}

async function carClickHandler(){
    const url = `/api/rsvp/${meetId}`;
    let id = $(this).attr("id");
    
    params = {
        carid: id
    }

    let resp = await axios.post(url, params);
    changeColor(resp);
    $('#cars-list').remove()
    return;
}
