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
        })
        .catch(function(err){
            console.error(err);
        });
    }

    function decrypt(){

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
    setTimeout(decrypt,500);
    // Export Key
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
    .catch(function(err){
        console.error(err);
    });
    setTimeout(function() {
        $.ajax({
            url: '/api/make_purchase_request',
            data: {
                "key": key_hex,
                "iv": iv_hex,
                "ciphertext": ciphertext_hex
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