var key = "";
var key_array = "";
var iv_hex = "";

window.onload = function (){
    // Generate Key
    window.crypto.subtle.generateKey(
        {
            name: "AES-CBC",
            length: 256, //can be  128, 192, or 256
        },
        true, //whether the key is extractable (i.e. can be used in exportKey)
        ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
    )
    .then(function(k){
        key = k;
    })
    .catch(function(err){
        console.error(err);
    });
}

function arrayToHex(array){
    result = "";
    array.map(function(i){
        result += ('0' + i.toString(16)).slice(-2);
    });
    return result;
}

function concateArray(a,b){
    var c = new (a.constructor)(a.length + b.length);
    c.set(a, 0);
    c.set(b, a.length);
    return c;
}


function makePurchaseRequest(oi){
    var data = "Hello World";
    var enc = new TextEncoder(); // always utf-8
    var array_data = enc.encode(data);
    var iv = window.crypto.getRandomValues(new Uint8Array(16));
    iv_hex = arrayToHex(iv);
    var ciphertext_array = "";
    var plaintext_array = "";
    var key_hex = "";
    var ciphertext_hex = "";
    function encrypt(){
        window.crypto.subtle.generateKey(
            {
                name: "AES-CBC",
                length: 256, //can be  128, 192, or 256
            },
            true, //whether the key is extractable (i.e. can be used in exportKey)
            ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
        )
        .then(function(k){
            key = k;
        })
        .then(function(){
            window.crypto.subtle.encrypt(
                {
                    name: "AES-CBC",
                    iv: iv,
                },
                key, //from generateKey or importKey above
                array_data //ArrayBuffer of data you want to encrypt
            )
            .then(function(encrypted){
                //returns an ArrayBuffer containing the encrypted data
                ciphertext_array = new Uint8Array(encrypted);
                console.log("Ciphertext: ", ciphertext_array);
                ciphertext_hex = arrayToHex(ciphertext_array);
                return ciphertext_hex;
            })
            .then(function(result){
                window.crypto.subtle.exportKey(
                    "raw", //can be "jwk" or "raw"
                    key //extractable must be true
                )
                .then(function(keydata){
                    var bufView = new Uint8Array(keydata);
                    key_array = bufView;
                    console.log("Key: ", key_array);
                    key_hex = arrayToHex(key_array);

                })
            })
            .then(function(result){
                decrypt()
            })
            .then(function(result){
                // Create Dual Signature
                oi_array = encode_info(order_info);
                pi_array = encode_info(payment_info)
                var pimd = "";
                var oimd = "";
                var pomd = "";

                window.crypto.subtle.digest(
                    {
                        name: "SHA-256",
                    },
                    oi_array //The data you want to hash as an ArrayBuffer
                )
                .then(function(hash){
                    oimd = new Uint8Array(hash);
                })
                .then(function(result){
                    window.crypto.subtle.digest(
                        {
                            name: "SHA-256",
                        },
                        pi_array //The data you want to hash as an ArrayBuffer
                    )
                    .then(function(hash){
                        pimd = new Uint8Array(hash);
                        return pimd;
                    })
                    .then(function(result){
                        console.log(result);
                        po = concateArray(oimd, pimd);
                        window.crypto.subtle.digest(
                            {
                                name: "SHA-256",
                            },
                            po //The data you want to hash as an ArrayBuffer
                        )
                        .then(function(hash){
                            pomd = new Uint8Array(hash);
                            pomd = arrayToHex(pimd)
                            oimd = arrayToHex(oimd)
                            pimd = arrayToHex(pimd)
                            console.log("POMD: ", pomd);
                            return pomd;
                        })
                        .then(function(result){
                            console.log("R: ", result);
                        })
                        .catch(function(err){
                            console.error(err);
                        });
                    })
                })
                .catch(function(err){
                    console.error(err);
                });

            })
            .then(function(result){
                console.log("RESULT: ", result);
            })
            .catch(function(err){
                console.error(err);
            });
        })
        .catch(function(err){
            console.error(err);
        });
    }

    function decrypt(){
        console.log("K: ", key);
        console.log( "iv", iv);
        console.log("ciphertext", ciphertext_array);
        window.crypto.subtle.decrypt(
            {
                name: "AES-CBC",
                iv: iv, //The initialization vector you used to encrypt
            },
            key, //from generateKey or importKey above
            ciphertext_array //ArrayBuffer of the data
        )
        .then(function(decrypted){
            //returns an ArrayBuffer containing the decrypted data
            console.log("Decrypted data: " + new Uint8Array(decrypted));
            console.log(new Uint8Array(decrypted));
            plaintext_array = new Uint8Array(decrypted);
            var enc = new TextDecoder("utf-8");

            console.log("Decrypted decoded-data: " + enc.decode(new Uint8Array(decrypted)));

        })
        .catch(function(err){
            console.error(err);
        });
    }
    setTimeout(encrypt,100);
//    setTimeout(decrypt,500);
    // Export Key

    var card_id = $("input[name=card-id]").val();
    setTimeout(function() {
        $.ajax({
            url: '/api/make_purchase_request',
            data: {
                "key": key_hex,
                "iv": iv_hex,
                "ciphertext": ciphertext_hex,
                "card-id": card_id
            },
            dataType: "json",
            type: 'POST',
            success: function(response) {
                if (response.data.status == "NO") {
                    alert("Không thanh toán đươc, hãy kiểm tra lại thông tin!");
//                    finished();
                    return false;
                } else {
                    alert("Cám ơn " + " đã mua hàng. Chúng tôi sẽ liên lạc để xác nhận và giao hàng nhanh nhất trong thời gian tới!");
//                    window.location.href = response.data.url;
//                    finished();
                }
            },
            error: function(error) {
                console.log("error");
//                finished();
            }
        });
    }, 2000);
}

var order_id = $("#order-id").text();
var order_sum = $('#order-sum').text();
var order_info = {
    "order_id": order_id,
    "order_sum": order_sum
};

var bank_name = $("input[name=bank-name]").val();
var card_id = $("input[name=card-id]").val();
var payment_info = {
    "bank_name": bank_name,
    "card_id": card_id
};


function encode_info(info_object){
    info_object = JSON.stringify(info_object);
    var enc = new TextEncoder();
    var result = enc.encode(info_object);
    return result;
}

function initPurchase(){
    var order_id = $("#order-id").text();
    var order_sum = $('#order-sum').text();
    var order_info = {
        "order_id": order_id,
        "order_sum": order_sum
    };

    var bank_name = $("input[name=bank-name]").val();
    var card_id = $("input[name=card-id]").val();
    var payment_info = {
        "bank_name": bank_name,
        "card_id": card_id
    };
//    dec = new TextDecoder();
//    oi = dec.decode(oi_array);
//    pi = dec.decode(pi_array);


    // Create Dual Signature
    oi_array = encode_info(order_info);
    pi_array = encode_info(payment_info)
    oi = arrayToHex(oi_array)
    pi = arrayToHex(pi_array)
    var pimd = "";
    var oimd = "";
    var pomd = "";

    window.crypto.subtle.digest(
        {
            name: "SHA-256",
        },
        oi_array //The data you want to hash as an ArrayBuffer
    )
    .then(function(hash){
        oimd = new Uint8Array(hash);
    })
    .then(function(result){
        window.crypto.subtle.digest(
            {
                name: "SHA-256",
            },
            pi_array //The data you want to hash as an ArrayBuffer
        )
        .then(function(hash){
            pimd = new Uint8Array(hash);
            return pimd;
        })
        .then(function(result){
            po = concateArray(oimd, pimd);
            console.log("PO: ", po);

            window.crypto.subtle.digest(
                {
                    name: "SHA-256",
                },
                po //The data you want to hash as an ArrayBuffer
            )
            .then(function(hash){
                pomd = new Uint8Array(hash);
                console.log("pomd", pomd);
                return pomd;
            })
            .then(function(result){
                var iv = window.crypto.getRandomValues(new Uint8Array(16));
                var key = "";
                var key_array = "";
                var iv_hex = arrayToHex(iv);
                var ciphertext_array = "";
                var plaintext_array = "";
                var key_hex = "";
                var ciphertext_hex = "";
                // Start Encrypt POMD
                window.crypto.subtle.generateKey(
                    {
                        name: "AES-CBC",
                        length: 256, //can be  128, 192, or 256
                    },
                    true, //whether the key is extractable (i.e. can be used in exportKey)
                    ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
                )
                .then(function(k){
                    key = k;
                })
                .then(function(){
                    window.crypto.subtle.encrypt(
                        {
                            name: "AES-CBC",
                            iv: iv,
                        },
                        key, //from generateKey or importKey above
                        pomd //ArrayBuffer of data you want to encrypt
                    )
                    .then(function(encrypted){
                        //returns an ArrayBuffer containing the encrypted data
                        ciphertext_array = new Uint8Array(encrypted);
                        console.log("Ciphertext: ", ciphertext_array);
                        ciphertext_hex = arrayToHex(ciphertext_array);
                        pomd = arrayToHex(pimd)
                        oimd = arrayToHex(oimd)
                        pimd = arrayToHex(pimd)
                        return ciphertext_hex;
                    })
                    .then(function(result){
                        window.crypto.subtle.exportKey(
                            "raw", //can be "jwk" or "raw"
                            key //extractable must be true
                        )
                        .then(function(keydata){
                            var bufView = new Uint8Array(keydata);
                            key_array = bufView;
                            console.log("Key: ", key_array);
                            console.log("IV: ", iv);
                            key_hex = arrayToHex(key_array);
                        })
                        .then(function(){
                            $.ajax({
                                url: '/api/make_purchase_request',
                                data: {
                                    "key": key_hex,
                                    "iv": iv_hex,
                                    "pomd": ciphertext_hex,
                                    "card-id": card_id,
                                    "oi": oi,
                                    "pi": pi,
                                    // "POMD": pomd
                                },
                                dataType: "json",
                                type: 'POST',
                                success: function(response) {
                                    if (response.data.status == "NO") {
                                        alert("Không thanh toán đươc, hãy kiểm tra lại thông tin!");
                                        return false;
                                    } else {
                                        alert("Cám ơn " + " đã mua hàng. Chúng tôi sẽ liên lạc để xác nhận và giao hàng nhanh nhất trong thời gian tới!");
                    //                    window.location.href = response.data.url;
                                    }
                                },
                                error: function(error) {
                                    console.log("error");
                                }
                            });
                        })
                        .catch(function(err){
                            console.error(err);
                        });
                    })
                    .catch(function(err){
                        console.error(err);
                    });
                }).catch(function(err){
                    console.error(err);
                });
            })
            .catch(function(err){
                console.error(err);
            });
        })
        .catch(function(err){
            console.error(err);
        });
    });
}
