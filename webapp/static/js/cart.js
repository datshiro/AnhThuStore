const cart_form = document.querySelector('#add-to-cart-form');
cart_form.addEventListener('submit', addToCart);

function addToCart(e){
    e.preventDefault();
    var action = $(this).attr('action');
    var list_val = $(this).serializeArray();
    var post_data = {};
    for (var i = 0; i < list_val.length; i++) {
        post_data[list_val[i].name] = list_val[i].value;
    }
    function updateCart(product_id, quantity){
        $.post("/shop/add-to-cart/"+ product_id + "&" + quantity)
                .done(function(data) {
                    location.reload();
                });
    }
    updateCart(post_data.product_id, post_data.quantity);
}