
$(document).ready(function() {
    retrieveData();
});

function retrieveData() {
    $.get("all", function(data, status) {
        console.log(data);
        if (!data) return;

        $(data).each(function (idx, item) {

            element_item_name = $("<div>").text(item.name);
            element_item_location = $("<div>").text(item.location);
            element_item_coffee = $("<div class='col-3'>").append( $("<i class='fa-solid fa-mug-hot'>") ).append( $("<span>").text(item.coffee_price));
            element_item_socket = $("<div class='col-3'>").append( $("<i class='fa-solid fa-plug-circle-bolt'></i>")).append( $("<span>").text( item.has_sockets?"Yes":"No"));
            element_item_toilet = $("<div class='col-3'>").append( $("<i class='fa-solid fa-restroom'></i>")).append( $("<span>").text(item.has_toilet?"Yes":"No"));
            element_item_wifi =   $("<div class='col-3'>").append( $("<i class='fa-solid fa-wifi'></i>")).append( $("<span>").text(item.has_wifi?"Yes":"No"));
            element_item_chair =  $("<div class='col-3'>").append( $("<i class='fa-solid fa-chair'></i>")).append( $("<span>").text(item.seats));

            element_item = $("<li class='list-group-item'>");
            div_item = $("<div class='container'>");
            element_item.append(div_item);
            div_item.append(
                $("<div class='row'>")
                    .append( $("<div class='col text-center'>").append( $("<img>").attr("src", item.img_url).addClass("rounded float-start").addClass("place") ) )
                    .append( $("<div class='col'>")
                            .append(element_item_name )
                            .append(element_item_location)
                            .append($("<div class='container'>").append($("<div class='row'>")
                                .append(element_item_coffee)
                                .append(element_item_socket)
                                .append(element_item_toilet)
                                .append(element_item_chair)
                            ))
                            )
                    .append( $(""))
                );
            $("#cafe_list").append(element_item);

            element_item.click(function() {
                window.location = "show/" + item.id;
            });
        })

    });
}
