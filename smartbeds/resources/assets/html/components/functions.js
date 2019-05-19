function reset() {

    fields.forEach(function (element) {
        element.removeClass("is-invalid");
        element.removeClass("is-valid");
    });

    fb.forEach(function (element) {
        element.removeClass("invalid-feedback");
        element.removeClass("valid-feedback");
        element.text("");
    });
}

function checkempty() {
    for (let i = 0; i < fields.length; i++) {
        if (fields[i].val() == "") {
            fields[i].addClass("is-invalid");
            fb[i].addClass("invalid-feedback");
            fb[i].text("Este campo no puede estar vacío");
            block_submit();
        }
    }
}

function checkbed() {
    $("#save_modal").attr("disabled", false);
    reset();
    checkempty();

    if (!checkip(ip.val())) {
        ip.addClass("is-invalid");
        ipfb.addClass("invalid-feedback");
        ipfb.text("La ip no es correcta, ha de estar entre 224.0.0.0 y 239.255.255.255");
        block_submit();
    } else if (ip.val() != "") {
        ip.addClass("is-valid");
        ipfb.addClass("valid-feedback");
        ipfb.text("Correcto");
    }

    if (bedname.val() != "") {
        bedname.addClass("is-valid");
        bednamefb.addClass("valid-feedback");
        bednamefb.text("Correcto");
    }

    if (port.val() != "") {
        port.addClass("is-valid");
        portfb.addClass("valid-feedback");
        portfb.text("Correcto");
    }

    checkmacuuid(mac_, macfb);
    checkmacuuid(uuid, uuidfb);


}

function block_submit() {
    $("#save_modal").attr("disabled", true);
}

function checkmacuuid(muid, fb) {
    let condicion = /^(([a-f0-9]){12})$/gmi;
    if (!condicion.test(muid.val())) {
        muid.addClass("is-invalid");
        fb.addClass("invalid-feedback");
        fb.text("El formato no es correcto, ha de ser: AABBCCDDEEFF");
        block_submit();
    } else if (muid.val() != "") {
        muid.addClass("is-valid");
        fb.addClass("valid-feedback");
        fb.text("Correcto");
    }

}

function checkip(ip) {
    let condicion = /^(([0-9]{1,3})\.){3}([0-9]{1,3})$/gm;
    if (condicion.test(ip)) {
        let ip_split = ip.split(".");
        for (let i = 0; i < ip_split.length; i++) {
            let n = parseInt(ip_split[i]);

            if (i === 0) {
                if (n < 224 || n > 239) {
                    return false;
                }
            } else if (n > 255) {
                return false;
            }

        }
    } else {
        return false;
    }
    return true;
}

$(document).ready(function () {
    fields.forEach(function (element) {
        element.keyup(checkbed)
    })
});
