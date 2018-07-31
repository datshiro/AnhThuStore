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

function initPurchase(order_info) {

    var bank_name = $("select[name=bank-name]").val();
    var card_id = $("input[name=card-id]").val();
    var payment_info = {
        "bank_name": bank_name,
        "card_id": card_id
    };

    oi = JSON.stringify(order_info);
    pi = JSON.stringify(payment_info);

    // Create Dual Signature
    oi_array = encode_info(order_info);
    pi_array = encode_info(payment_info)

    var pimd = "";
    var oimd = "";
    var pomd = "";
    var merchant_part = "";
    var gateway_part = "";
    var k1 = "";
    var k1_encrypted = "";
    var dual_signature = "";
    var k2 = "";
    var k2_encrypted = "";
    var merchant_part_encrypted = "";
    var gateway_part_encrypted = "";
    var iv1 = "";
    var iv2 = "";

    hash256(oi_array).then(function(hash) {
            oimd = new Uint8Array(hash);
            console.log("OIMD", oimd)
        })
    .then(function(result) {
        hash256(pi_array).then(function(hash) {
                pimd = new Uint8Array(hash);
                console.log("PIMD", pimd)
                return pimd;
            })
            .then(function(result) {
                po = concateArray(oimd, pimd);
                console.log("PO: ", po);

                hash256(po).then(function(hash) {
                        pomd = new Uint8Array(hash);
                        console.log("pomd", pomd);
                        return pomd;
                    })
                    .then(function(result) {
                        iv1 = window.crypto.getRandomValues(new Uint8Array(16));
                        var key_array = "";
                        var ciphertext_array = "";
                        var plaintext_array = "";
                        var key_hex = "";
                        var ciphertext_hex = "";
                        // Start Encrypt POMD
                        genKey().then(function(k) {
                                k1 = k;
                                console.log("Key DS", k1)
                            })
                            .then(function() {
                                window.crypto.subtle.encrypt({
                                            name: "AES-CBC",
                                            iv: iv1,
                                        },
                                        k1, //from generateKey or importKey above
                                        pomd //ArrayBuffer of data you want to encrypt
                                    )
                                .then(function(encrypted) {
                                    //returns an ArrayBuffer containing the encrypted data
                                    var dual_signature_array = new Uint8Array(encrypted);
                                    console.log("dual_signature_array", dual_signature_array)
                                    dual_signature = arrayToHex(dual_signature_array)
                                    console.log("dual_signature", dual_signature)

                                    oimd = arrayToHex(oimd)
                                    pimd = arrayToHex(pimd)
                                })
                                .then(function(result) {
                                    exportKey(k1).then(function(key_array){
                                        key_ds_array = key_array;
                                        console.log("KEY_DS_ARRAY", key_ds_array);
                                    })
                                    // Got Dual Signature
                                    // Create Merchant Part
                                    .then(function() {
                                        merchant_part = {
                                            "oi": oi,
                                            "ds": dual_signature,
                                            "pimd": pimd,
                                        };
                                        gateway_part={
                                            "pi": pi,
                                            "ds": dual_signature,
                                            "oimd": oimd
                                        };
                                        genKey().then(function(k) {
                                            k2 = k;
                                            iv2 = window.crypto.getRandomValues(new Uint8Array(16));
                                            // Encrypt merchant_part with k2
                                            window.crypto.subtle.encrypt({
                                                        name: "AES-CBC",
                                                        iv: iv2,
                                                    },
                                                    k2, //from generateKey or importKey above
                                                    encode_info(gateway_part) //ArrayBuffer of data you want to encrypt
                                                )
                                                .then(function(encrypted) {
                                                    // Export K2
                                                    exportKey(k2).then(function(key_array){
                                                        k2 = key_array;
                                                        console.log("K2", k2);
                                                    })
                                                    gateway_part_encrypted = new Uint8Array(encrypted);
                                                    // Import Kum pemKey
                                                    crypto.subtle.importKey("spki", convertPemToBinary($('#kupg').val()), encryptAlgorithm, false, ["encrypt"]).
                                                    then(function(key) {
                                                            // Encrypt K2 with Kum
                                                            crypto.subtle.encrypt({
                                                                    name: "RSA-OAEP"
                                                                },
                                                                key,
                                                                k2).
                                                            then(function(cipherData) {
                                                                k2_encrypted = new Uint8Array(cipherData);
                                                                console.log("K2_Encrypted", k2_encrypted);
                                                                console.log("gateway_part_encrypted", gateway_part_encrypted);
                                                                console.log("IV1", iv1);
                                                                console.log("DS", dual_signature);
                                                            }).
                                                            then(encryptKey1(k1).then(function(encrypted){
                                                                    k1_encrypted = encrypted;
                                                                })
                                                                // Send Ajax to Server
                                                                .then(function() {
                                                                    console.log("START SEND AJAX");
                                                                    $.ajax({
                                                                        url: '/api/make_purchase_request',
                                                                        data: {
                                                                            "pomd": arrayToHex(pomd),
                                                                            "card-id": card_id,
                                                                            "oi": oi,
                                                                            "pi": pi,
                                                                            "po": arrayToHex(po),
                                                                            "oimd": oimd,
                                                                            "pimd": pimd,
                                                                            "k2_encrypted": arrayToHex(k2_encrypted),
                                                                            "merchant_part": JSON.stringify(merchant_part),
                                                                            "gateway_part_encrypted": arrayToHex(gateway_part_encrypted),
                                                                            "k1_encrypted": arrayToHex(k1_encrypted),
                                                                            "iv1": arrayToHex(iv1),
                                                                            "iv2": arrayToHex(iv2),
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
                                                            )
                                                            .catch(function(err) {
                                                                console.error(err);
                                                            });
                                                        })
                                                        .catch(function(err) {
                                                            console.error(err);
                                                        });
                                                })
                                                .catch(function(err) {
                                                    console.error(err);
                                                });

                                        })
                                        .catch(function(err) {
                                            console.error(err);
                                        });
                                    })
                                    .catch(function(err) {
                                        console.error(err);
                                    });
                                })
                                .catch(function(err) {
                                    console.error(err);
                                });
                            })
                            .catch(function(err) {
                                console.error(err);
                            });
                    })
                    .catch(function(err) {
                        console.error(err);
                    });
            })
            .catch(function(err) {
                console.error(err);
            });
    })
    .catch(function(err) {
        console.error(err);
    });
}

var encryptAlgorithm = {
  name: "RSA-OAEP",
  hash: {
    name: "SHA-1"
  }
};

function arrayBufferToBase64String(arrayBuffer) {
  var byteArray = new Uint8Array(arrayBuffer)
  var byteString = '';
  for (var i=0; i<byteArray.byteLength; i++) {
    byteString += String.fromCharCode(byteArray[i]);
  }
  return btoa(byteString);
}

function base64StringToArrayBuffer(b64str) {
  var byteStr = atob(b64str);
  var bytes = new Uint8Array(byteStr.length);
  for (var i = 0; i < byteStr.length; i++) {
    bytes[i] = byteStr.charCodeAt(i);
  }
  return bytes.buffer;
}

function textToArrayBuffer(str) {
  var buf = unescape(encodeURIComponent(str)); // 2 bytes for each char
  var bufView = new Uint8Array(buf.length);
  for (var i=0; i < buf.length; i++) {
    bufView[i] = buf.charCodeAt(i);
  }
  return bufView;
}

function convertPemToBinary(pem) {
  var lines = pem.split('\\n');
  var encoded = '';
  for(var i = 0;i < lines.length;i++){
    if (lines[i].trim().length > 0 &&
        lines[i].indexOf('-BEGIN RSA PRIVATE KEY-') < 0 &&
        lines[i].indexOf('-BEGIN RSA PUBLIC KEY-') < 0 &&
        lines[i].indexOf('-BEGIN PUBLIC KEY-') < 0 &&
        lines[i].indexOf('-END PUBLIC KEY-') < 0 &&
        lines[i].indexOf('-END RSA PRIVATE KEY-') < 0 &&
        lines[i].indexOf('-END RSA PUBLIC KEY-') < 0) {
      encoded += lines[i].trim();
    }
  }
  return base64StringToArrayBuffer(encoded);
}

function genKey(){
    return new Promise(function(resolve){
        var generator = window.crypto.subtle.generateKey({
                                name: "AES-CBC",
                                length: 256, //can be  128, 192, or 256
                            },
                            true, //whether the key is extractable (i.e. can be used in exportKey)
                            ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
                        );
        generator.then(function(key){
            resolve(key);
        });
    });
}

function hash256(array_data){
    return new Promise(function(resolve){
        var hasher = window.crypto.subtle.digest({
                name: "SHA-256",
            },
            array_data //The data you want to hash as an ArrayBuffer
        );
        hasher.then(function(hash){
            resolve(hash);
        })
    });

}

function exportKey(key_obj){
    return new Promise(function(resolve){
        window.crypto.subtle.exportKey(
            "raw", //can be "jwk" or "raw"
            key_obj //extractable must be true
        )
        .then(function(keydata) {
            var bufView = new Uint8Array(keydata);
            key_array = bufView;
            return key_array
        }).then(function(key_array){
            resolve(key_array);
        })
    });
}

function encryptKey1(k1){
    return new  Promise(function(resolve){
        // Import Kum pemKey
        var k1_encrypted = "";
        crypto.subtle.importKey("spki", convertPemToBinary($('#kum').val()), encryptAlgorithm, false, ["encrypt"]).
        then(function(key) {
            // Encrypt K1 with Kupg
            exportKey(k1).then(function(key_array){
                k1 = key_array;
                crypto.subtle.encrypt({
                        name: "RSA-OAEP"
                    },
                    key,
                    k1).
                then(function(cipherData) {
                        k1_encrypted = new Uint8Array(cipherData);
                        console.log("K1_Encrypted", k1_encrypted);
                        return k1_encrypted;
                }).
                then(function(gateway){
                    resolve(gateway);
                })
            })
        })
    });
}

function arrayToB64(arr){
    return btoa(arr);
}

function b64ToArray(b64str){
    return atob(b64str);
}

//function merchantPart(merchant_part, k1, iv){
//    return new Promise(function(resolve){
//         var gateway_part_encrypted = "";
//         var k1_encrypted = "";
//
//        // Encrypt gateway_part with k1
//        window.crypto.subtle.encrypt({
//                name: "AES-CBC",
//                iv: iv,
//            },
//            k1, //from generateKey or importKey above
//            encode_info(merchant_part) //ArrayBuffer of data you want to encrypt
//        )
//        .then(function(encrypted) {
//            // Export K2
//            exportKey(k1).then(function(key_array){
//                k1 = key_array;
//            })
//            merchant_part_encrypted = new Uint8Array(encrypted);
//            // Import Kum pemKey
//            crypto.subtle.importKey("spki", convertPemToBinary($('#kum').val()), encryptAlgorithm, false, ["encrypt"]).
//            then(function(key) {
//                // Encrypt K1 with Kupg
//                crypto.subtle.encrypt({
//                        name: "RSA-OAEP"
//                    },
//                    key,
//                    k1).
//                then(function(cipherData) {
//                        k1_encrypted = new Uint8Array(cipherData);
//                        console.log("K1_Encrypted", k1_encrypted);
//                        console.log("merchant_part_encrypted", merchant_part_encrypted);
//                        var gateway = {
//                            "k1_encrypted": k1_encrypted,
//                            "merchant_part_encrypted": merchant_part_encrypted
//                        };
//                        return gateway;
//                }).
//                then(function(gateway){
//                    resolve(gateway);
//                })
//            })
//        })
//    });
//}