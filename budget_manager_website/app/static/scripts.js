$(document).ready( function () {
    $('#table').DataTable({
        "order": [[ 0, "desc" ]],
        searching: false
    }
    );
});

// document.querySelector("#table").scrollIntoView();
// document.location.hash = `#table`;