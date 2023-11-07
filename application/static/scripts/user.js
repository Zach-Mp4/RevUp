$(document).ready(function () {
    $('i').on('click', clickHandler);     
});

async function clickHandler(){
    $parent = $(this).parent();
    let id = $(this).attr('id');
    let resp = await axios.delete(`/api/cars/delete/${id}`);
    $parent.remove();
}