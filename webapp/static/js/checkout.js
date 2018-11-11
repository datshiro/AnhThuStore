var key = "";
var key_array = "";
var iv_hex = "";

window.onload = function () {
    // Generate Key
    window.crypto.subtle.generateKey(
        {
            name: "AES-CBC",
            length: 256, //can be  128, 192, or 256
        },
        true, //whether the key is extractable (i.e. can be used in exportKey)
        ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
    )
        .then(function (k) {
            key = k;
        })
        .catch(function (err) {
            console.error(err);
        });
}

function arrayToHex(array) {
    result = "";
    array.map(function (i) {
        result += ('0' + i.toString(16)).slice(-2);
    });
    return result;
}

function concateArray(a, b) {
    var c = new (a.constructor)(a.length + b.length);
    c.set(a, 0);
    c.set(b, a.length);
    return c;
}


function makePurchaseRequest(oi) {
    var data = "Hello World";
    var enc = new TextEncoder(); // always utf-8
    var array_data = enc.encode(data);
    var iv = window.crypto.getRandomValues(new Uint8Array(16));
    iv_hex = arrayToHex(iv);
    var ciphertext_array = "";
    var plaintext_array = "";
    var key_hex = "";
    var ciphertext_hex = "";
    function encrypt() {
        window.crypto.subtle.generateKey(
            {
                name: "AES-CBC",
                length: 256, //can be  128, 192, or 256
            },
            true, //whether the key is extractable (i.e. can be used in exportKey)
            ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
        )
            .then(function (k) {
                key = k;
            })
            .then(function () {
                window.crypto.subtle.encrypt(
                    {
                        name: "AES-CBC",
                        iv: iv,
                    },
                    key, //from generateKey or importKey above
                    array_data //ArrayBuffer of data you want to encrypt
                )
                    .then(function (encrypted) {
                        //returns an ArrayBuffer containing the encrypted data
                        ciphertext_array = new Uint8Array(encrypted);
                        console.log("Ciphertext: ", ciphertext_array);
                        ciphertext_hex = arrayToHex(ciphertext_array);
                        return ciphertext_hex;
                    })
                    .then(function (result) {
                        window.crypto.subtle.exportKey(
                            "raw", //can be "jwk" or "raw"
                            key //extractable must be true
                        )
                            .then(function (keydata) {
                                var bufView = new Uint8Array(keydata);
                                key_array = bufView;
                                console.log("Key: ", key_array);
                                key_hex = arrayToHex(key_array);

                            })
                    })
                    .then(function (result) {
                        decrypt()
                    })
                    .then(function (result) {
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
                            .then(function (hash) {
                                oimd = new Uint8Array(hash);
                            })
                            .then(function (result) {
                                window.crypto.subtle.digest(
                                    {
                                        name: "SHA-256",
                                    },
                                    pi_array //The data you want to hash as an ArrayBuffer
                                )
                                    .then(function (hash) {
                                        pimd = new Uint8Array(hash);
                                        return pimd;
                                    })
                                    .then(function (result) {
                                        console.log(result);
                                        po = concateArray(oimd, pimd);
                                        window.crypto.subtle.digest(
                                            {
                                                name: "SHA-256",
                                            },
                                            po //The data you want to hash as an ArrayBuffer
                                        )
                                            .then(function (hash) {
                                                pomd = new Uint8Array(hash);
                                                pomd = arrayToHex(pimd)
                                                oimd = arrayToHex(oimd)
                                                pimd = arrayToHex(pimd)
                                                console.log("POMD: ", pomd);
                                                return pomd;
                                            })
                                            .then(function (result) {
                                                console.log("R: ", result);
                                            })
                                            .catch(function (err) {
                                                console.error(err);
                                            });
                                    })
                            })
                            .catch(function (err) {
                                console.error(err);
                            });

                    })
                    .then(function (result) {
                        console.log("RESULT: ", result);
                    })
                    .catch(function (err) {
                        console.error(err);
                    });
            })
            .catch(function (err) {
                console.error(err);
            });
    }

    function decrypt() {
        console.log("K: ", key);
        console.log("iv", iv);
        console.log("ciphertext", ciphertext_array);
        window.crypto.subtle.decrypt(
            {
                name: "AES-CBC",
                iv: iv, //The initialization vector you used to encrypt
            },
            key, //from generateKey or importKey above
            ciphertext_array //ArrayBuffer of the data
        )
            .then(function (decrypted) {
                //returns an ArrayBuffer containing the decrypted data
                console.log("Decrypted data: " + new Uint8Array(decrypted));
                console.log(new Uint8Array(decrypted));
                plaintext_array = new Uint8Array(decrypted);
                var enc = new TextDecoder("utf-8");

                console.log("Decrypted decoded-data: " + enc.decode(new Uint8Array(decrypted)));

            })
            .catch(function (err) {
                console.error(err);
            });
    }
    setTimeout(encrypt, 100);
    //    setTimeout(decrypt,500);
    // Export Key

    var card_id = $("input[name=card-id]").val();
    setTimeout(function () {
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
            success: function (response) {
                if (response.data.status == "NO") {
                    alert("Không thanh toán đươc, hãy kiểm tra lại thông tin!");
                    //                    finished();
                    return false;
                } else {
                    alert("Cám ơn " + " đã mua hàng. Chúng tôi sẽ liên lạc để xác nhận và giao hàng nhanh nhất trong thời gian tới!");
                    //                    window.location.href = response.data.url;hang
                    //                    finished();
                }
            },
            error: function (error) {
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


function encode_info(info_object) {
    info_object = JSON.stringify(info_object);
    var enc = new TextEncoder();
    var result = enc.encode(info_object);
    return result;
}

async function initPurchase(order_info) {

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
    try {
        let oi_hash = await hash256(oi_array);
        oimd = new Uint8Array(oi_hash);
        console.log("OIMD", oimd);

        let pi_hash = await hash256(pi_array);
        pimd = new Uint8Array(pi_hash);
        console.log("PIMD", pimd);

        po = concateArray(oimd, pimd);
        console.log("PO: ", po);
        let po_hash = await hash256(po);
        pomd = new Uint8Array(po_hash);
        console.log("pomd", pomd);

        iv1 = window.crypto.getRandomValues(new Uint8Array(16));
        k1 = await genKey();
        console.log("Key DS", k1);
        let encrypted_pomd = window.crypto.subtle.encrypt({
            name: "AES-CBC",
            iv: iv1,
        },
            k1, //from generateKey or importKey above
            pomd //ArrayBuffer of data you want to encrypt
        );

        //returns an ArrayBuffer containing the encrypted data
        let dual_signature_array = new Uint8Array(encrypted_pomd);
        console.log("dual_signature_array", dual_signature_array);
        dual_signature = arrayToHex(dual_signature_array);
        console.log("dual_signature", dual_signature);
        pimd = arrayToHex(pimd);
        oimd = arrayToHex(oimd);
        let key_ds_array = await exportKey(k1);
        console.log("KEY_DS_ARRAY", key_ds_array);
        // Got Dual Signature
        // Create Merchant Part
        merchant_part = {
            "oi": oi,
            "ds": dual_signature,
            "pimd": pimd,
        };
        gateway_part = {
            "pi": pi,
            "ds": dual_signature,
            "oimd": oimd
        };
        k2 = await genKey();
        iv2 = window.crypto.getRandomValues(new Uint8Array(16));
        // Encrypt merchant_part with k2
        let encrypted_gateway_part_array = await window.crypto.subtle.encrypt({
            name: "AES-CBC",
            iv: iv2,
        },
            k2, //from generateKey or importKey above
            encode_info(gateway_part) //ArrayBuffer of data you want to encrypt
        );
        // Export K2
        k2 = await exportKey(k2);
        gateway_part_encrypted = new Uint8Array(encrypted_gateway_part_array);
        // Import Kum pemKey
        let key_to_encrypt_k2 = await crypto.subtle.importKey("spki", convertPemToBinary($('#kupg').val()), encryptAlgorithm, false, ["encrypt"]);
        let encrypted_k2_array = await crypto.subtle.encrypt({
            name: "RSA-OAEP"
        },
            key_to_encrypt_k2,
            k2);
        k2_encrypted = new Uint8Array(encrypted_k2_array);
        console.log("K2_Encrypted", k2_encrypted);
        console.log("gateway_part_encrypted", gateway_part_encrypted);
        console.log("IV1", iv1);
        console.log("DS", dual_signature);
        k1_encrypted = await encryptKey1(k1);
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
            success: function (response) {
                if (response.data.status == "NO") {
                    alert("Không thanh toán đươc, hãy kiểm tra lại thông tin!\n" + response.data.message);
                    return false;
                } else {
                    // var authdata = response.data.authdata
                    // if (authdata != 'everything is good') {
                    //     alert('something went wrong while starting transaction');
                    // }
                    if (response.data.action == 'password') {
                        var authdata_signature = base64StringToArrayBuffer(response.data.b64_authdata_signature);
                        var authdata_encrypted = base64StringToArrayBuffer(response.data.b64_authdata_encrypted);
                        var k5_b64_encrypted = base64StringToArrayBuffer(response.data.b64_k5_b64_encrypted);
                        var bankcertificate = base64StringToArrayBuffer(response.data.b64_bankcertificate);
                        var kuis = atob(response.data.b64_kuis);

                        bankcertificate = new TextDecoder().decode(bankcertificate);
                        if (bankcertificate != 'VCB-DATSHIRO') {
                            alert("Failed Transaction! Please Try Again!");
                            return;
                        }

                        console.log('authdata_signature', authdata_signature);
                        console.log('authdata_encrypted', authdata_encrypted);
                        console.log('k5_b64_encrypted', k5_b64_encrypted);
                        k5 = await decryptK5_B64(k5_b64_encrypted, k1);
                        let decrypted_authdata = await decrypt_aes_from_merchant(k5, authdata_encrypted);

                        // Verify Signature
                        let isvalid = await verify_authdata(decrypted_authdata, authdata_signature);
                        console.log("isvalid", isvalid);
                        if (isvalid) {
                            decrypted_authdata = new TextDecoder().decode(decrypted_authdata);
                            if (decrypted_authdata == 'everything is good') {
                                var password = prompt("Please enter your card password");
                                if (password != null) {
                                    send_password(password, kuis);
                                }
                            } else {
                                alert("Failed Transaction! Please Try Again!");
                            }
                        }

                    }
                }
            },
            error: function (error) {
                console.log("error");
            }
        });
    } catch (error) {
        console.error(error);
    }
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
    for (var i = 0; i < byteArray.byteLength; i++) {
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
    for (var i = 0; i < buf.length; i++) {
        bufView[i] = buf.charCodeAt(i);
    }
    return bufView;
}

function convertPemToBinary(pem, is_bytes = true) {
    var lines = pem.split('\\n');
    if (is_bytes == false) {
        var lines = pem.split('\n');
    }
    var encoded = '';
    for (var i = 0; i < lines.length; i++) {
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

function genKey() {
    return new Promise(function (resolve) {
        var generator = window.crypto.subtle.generateKey({
            name: "AES-CBC",
            length: 256, //can be  128, 192, or 256
        },
            true, //whether the key is extractable (i.e. can be used in exportKey)
            ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
        );
        generator.then(function (key) {
            resolve(key);
        });
    });
}

function hash256(array_data) {
    return new Promise(function (resolve) {
        var hasher = window.crypto.subtle.digest({
            name: "SHA-256",
        },
            array_data //The data you want to hash as an ArrayBuffer
        );
        hasher.then(function (hash) {
            resolve(hash);
        })
    });

}

function exportKey(key_obj) {
    return new Promise(function (resolve) {
        window.crypto.subtle.exportKey(
            "raw", //can be "jwk" or "raw"
            key_obj //extractable must be true
        )
            .then(function (keydata) {
                var bufView = new Uint8Array(keydata);
                key_array = bufView;
                return key_array
            }).then(function (key_array) {
                resolve(key_array);
            })
    });
}

function encrypt_rsa(pem_key, message) {
    return new Promise(
        function (resolve) {
            var encrypted = "";
            console.log("pem_key", pem_key);
            crypto.subtle.importKey("spki", convertPemToBinary(pem_key, false), encryptAlgorithm, false, ["encrypt"]).
                then(function (key) {
                    crypto.subtle.encrypt({
                        name: "RSA-OAEP"
                    },
                        key,
                        new TextEncoder().encode(message)
                    ).
                        then(function (cipherData) {
                            cipherData = new Uint8Array(cipherData);
                            console.log("cipherData", cipherData);
                            resolve(cipherData);
                        })
                        .catch(function (err) {
                            console.error(err);
                        });
                })
        }
    );
}

function encryptKey1(k1) {
    return new Promise(function (resolve) {
        // Import Kum pemKey
        var k1_encrypted = "";
        crypto.subtle.importKey("spki", convertPemToBinary($('#kum').val()), encryptAlgorithm, false, ["encrypt"]).
            then(function (key) {
                // Encrypt K1 with Kupg
                exportKey(k1).then(function (key_array) {
                    k1 = key_array;
                    crypto.subtle.encrypt({
                        name: "RSA-OAEP"
                    },
                        key,
                        k1).
                        then(function (cipherData) {
                            k1_encrypted = new Uint8Array(cipherData);
                            console.log("K1_Encrypted", k1_encrypted);
                            return k1_encrypted;
                        }).
                        then(function (gateway) {
                            resolve(gateway);
                        })
                })
            })
    });
}

function encryptKey6(k6, pem_key) {
    return new Promise(function (resolve) {
        // Import Kum pemKey
        var k6_encrypted = "";
        crypto.subtle.importKey("spki", convertPemToBinary(pem_key), encryptAlgorithm, false, ["encrypt"]).
            then(function (key) {
                // Encrypt K1 with Kupg
                exportKey(k6).then(function (key_array) {
                    k6 = key_array;
                    crypto.subtle.encrypt({
                        name: "RSA-OAEP"
                    },
                        key,
                        k6).
                        then(function (cipherData) {
                            k6_encrypted = new Uint8Array(cipherData);
                            console.log("K6_Encrypted", k6_encrypted);
                            resolve(k6_encrypted);
                        })
                })
            })
    });
}

function decryptK5_B64(k5_b64_encrypted, k1) {
    return new Promise(
        function (resolve) {
            k5_b64_encrypted = new Uint8Array(k5_b64_encrypted);
            window.crypto.subtle.decrypt(
                {
                    name: "AES-CBC",
                    iv: k5_b64_encrypted.slice(0, 16), //The initialization vector you used to encrypt
                },
                k1,
                k5_b64_encrypted.slice(16))
                .then(function (decrypted) {
                    //returns an ArrayBuffer containing the decrypted data

                    // Decode Base64
                    var byteArray = new Uint8Array(decrypted);
                    var byteString = '';
                    for (var i = 0; i < byteArray.byteLength; i++) {
                        byteString += String.fromCharCode(byteArray[i]);
                    }
                    k5 = base64StringToArrayBuffer(byteString);
                    console.log("k5", k5);
                    resolve(k5);
                })
        }
    );
}

function decrypt_aes_from_merchant(key, encrypted) {
    return new Promise(
        function (resolve) {
            window.crypto.subtle.importKey(
                "raw", //can be "jwk" or "raw"
                key,
                {   //this is the algorithm options
                    name: "AES-CBC",
                },
                true, //whether the key is extractable (i.e. can be used in exportKey)
                ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
            )
                .then(function (key) {
                    window.crypto.subtle.decrypt(
                        {
                            name: "AES-CBC",
                            iv: encrypted.slice(0, 16), //The initialization vector you used to encrypt
                        },
                        key,
                        encrypted.slice(16))
                        .then(function (decrypted) {
                            //returns an ArrayBuffer containing the decrypted data
                            decrypted = new Uint8Array(decrypted);
                            //                    console.log("decrypted", decrypted, arrayToHex(decrypted));
                            //                    decrypted_string = new TextDecoder().decode(decrypted);
                            resolve(decrypted);
                        })
                })

        }
    );
}

function verify_authdata(authdata, authdata_signature) {
    return new Promise(
        function (resolve) {
            crypto.subtle.importKey("spki", convertPemToBinary($('#kum').val()),
                {   //these are the algorithm options
                    name: "RSA-PSS",
                    hash: { name: "SHA-256" }, //can be "SHA-1", "SHA-256", "SHA-384", or "SHA-512"
                },
                false,
                ["verify"]).
                then(function (key) {
                    console.log("authdata", authdata);
                    console.log("authdata_signature", authdata_signature);

                    window.crypto.subtle.verify(
                        {
                            name: "RSA-PSS",
                            saltLength: 20, //the length of the salt
                        },
                        key, //from generateKey or importKey above
                        authdata_signature, //ArrayBuffer of the signature
                        authdata //ArrayBuffer of the data
                    )
                        .then(function (isvalid) {
                            resolve(isvalid);
                        })
                })

        }
    );
}

function send_password(password, kuis) {
    return new Promise(
        function (resolve) {
            var password_kuisencrypted = "";
            var password_kuisencrypted_hashed = "";
            var pwd_kuisencrypted_and_hashed = "";
            var pwd_kuisencrypted_and_hashed_k6encrypted = "";
            var k6 = "";
            var k6_encrypted_kupg = "";
            var k6_encrypted_kum = "";
            var iv6 = window.crypto.getRandomValues(new Uint8Array(16));
            var authdata = "hi this is my password";
            var authdata_hashed = "";
            var authdata_and_hashed_k6encrypted = "";
            var kupg = $('#kupg').val();
            var kum = $('#kum').val();

            // Encrypt Password
            encrypt_rsa(kuis, password).then(function (encrypted) {
                encrypted = new Uint8Array(encrypted);
                password_kuisencrypted = encrypted;

                // Hash Encrypted Password
                hash256(password_kuisencrypted).then(function (hash) {
                    hash = new Uint8Array(hash);
                    password_kuisencrypted_hashed = hash;           //32 length
                    pwd_kuisencrypted_and_hashed = concateArray(password_kuisencrypted, password_kuisencrypted_hashed);

                    // Encrypt Combined Part
                    genKey().then(function (k) {
                        k6 = k;
                        console.log("Key k6", k6)
                    })
                        .then(function () {
                            window.crypto.subtle.encrypt({
                                name: "AES-CBC",
                                iv: iv6,
                            },
                                k6, //from generateKey or importKey above
                                pwd_kuisencrypted_and_hashed //ArrayBuffer of data you want to encrypt
                            )
                                .then(function (encrypted) {
                                    encrypted = new Uint8Array(encrypted);
                                    pwd_kuisencrypted_and_hashed_k6encrypted = encrypted
                                })
                                // Encrypt K6 with kupg
                                .then(function () {
                                    encryptKey6(k6, kupg).then(function (encrypted) {
                                        k6_encrypted_kupg = encrypted;
                                    }).
                                        // Hash Authdata
                                        then(function () {
                                            var authdata_array = new TextEncoder().encode(authdata);
                                            hash256(authdata_array).then(function (hash) {
                                                authdata_hashed = new Uint8Array(hash);
                                                console.log("authdata_hashed", authdata_hashed);

                                                var authdata_and_hashed = concateArray(authdata_array, authdata_hashed);
                                                // Encrypt authdata_and_hashed with K6
                                                window.crypto.subtle.encrypt({
                                                    name: "AES-CBC",
                                                    iv: iv6,
                                                },
                                                    k6, //from generateKey or importKey above
                                                    authdata_and_hashed //ArrayBuffer of data you want to encrypt
                                                )
                                                    .then(function (encrypted) {
                                                        encrypted = new Uint8Array(encrypted);
                                                        authdata_and_hashed_k6encrypted = encrypted

                                                        // Encrypt K6 with kum
                                                        encryptKey6(k6, kum).then(function (encrypted) {
                                                            k6_encrypted_kum = encrypted;
                                                        }).
                                                            // Send all to merchant
                                                            then(function () {
                                                                $.ajax({
                                                                    url: '/api/password',
                                                                    data: {
                                                                        "k6_encrypted_kum": arrayToHex(k6_encrypted_kum),
                                                                        "k6_encrypted_kupg": arrayToHex(k6_encrypted_kupg),
                                                                        "iv6": arrayToHex(iv6),
                                                                        "authdata_and_hashed_k6encrypted": arrayToHex(authdata_and_hashed_k6encrypted),
                                                                        "pwd_kuisencrypted_and_hashed_k6encrypted": arrayToHex(pwd_kuisencrypted_and_hashed_k6encrypted),
                                                                    },
                                                                    dataType: "json",
                                                                    type: 'POST',
                                                                    success: function (response) {
                                                                        if (response.data.status == "NO") {
                                                                            alert("Không thanh toán đươc, hãy kiểm tra lại thông tin!\n" + response.data.message);
                                                                            return false;
                                                                        } else {
                                                                            alert(response.data.payment_response);
                                                                            alert("Cám ơn " + " đã mua hàng. Chúng tôi sẽ liên lạc để xác nhận và giao hàng nhanh nhất trong thời gian tới!");
                                                                            console.log("url", response.data.url);
                                                                            window.location.href = response.data.url;
                                                                        }
                                                                    },
                                                                    error: function (error) {
                                                                        console.log("error");
                                                                    }
                                                                });
                                                            })
                                                    })
                                            })
                                        })
                                })
                        })
                })
            })
                .catch(function (err) {
                    console.error(err);
                });
        }
    );
}

function arrayToB64(arr) {
    return btoa(arr);
}

function b64ToArray(b64str) {
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