$(function () {

        // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // List Pets
    // ****************************************

    $("#list-btn").click(function () {

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer Name</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-2">Product Name</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Is Urgent?</th>'
            table += '</tr></thead><tbody>'
            let firstShopcart = "";
            let row_count = 0;
            for (let i = 0; i < res.length; i++) {
                let shopcart = res[i];
                table += `<tr id="row_${row_count}"><td>${shopcart.id}</td><td>${shopcart.customer_name}</td></tr>`;
                row_count++;
                for (let j = 0; j < shopcart.items.length; j++){
                    let item = shopcart.items[j];
                    table += `<tr id="row_${row_count}"><td></td><td></td><td>${item.id}</td><td>${item.name}</td><td>${item.description}</td><td>${item.price}</td><td>${item.quantity}</td><td>${item.is_urgent}</td></tr>`;
                    row_count++;
                }
                if (i == 0) {
                    firstShopcart = shopcart;
                }
            }
            table += '</tbody></table>';
            $("#results").append(table);

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });
})
