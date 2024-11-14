$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcarts_id").val(res.id);
        $("#shopcarts_customer_name").val(res.customer_name);
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#shopcarts_customer_name").val("");
    }
    

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let customer_name = $("#shopcarts_customer_name").val();

        let data = {
            "customer_name": customer_name,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcarts_id = $("#shopcarts_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/shopcarts/${shopcarts_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Empty a Shopcart
    // ****************************************

    $("#empty-btn").click(function () {

        let shopcarts_id = $("#shopcarts_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/shopcarts/${shopcarts_id}/empty`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let id = $("#shopcarts_id").val();
        let customer_name = $("#shopcarts_customer_name").val();

        let data = {
            "customer_name": customer_name,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/shopcarts/${id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let id = $("#shopcarts_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/shopcarts/${id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // List Shopcarts
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

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#shopcarts_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

})
