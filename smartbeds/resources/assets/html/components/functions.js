function correcto(data, textStatus, jQxhr) {
    location.reload();
}

function incorrecto(data, textStatus, jQxhr) {
    let msg = JSON.parse(data.responseText).message;
    if (data.status === 418) {
        show_modal_error("Operación no válida",);
    } else {
        $("#errormsg").text(msg);
    }
}

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

function checkstart() {
    $("#save_modal").attr("disabled", false);

    reset();
    checkempty();
}

function campo_correcto(field, fb) {
    field.addClass("is-valid");
    fb.addClass("valid-feedback");
    fb.text("Correcto");
}

function campo_incorrecto(field, fb, text) {
    field.addClass("is-invalid");
    fb.addClass("invalid-feedback");
    fb.text(text);
    block_submit();
}

function checkuser() {
    checkstart();

    if (nick.val() != "") {
        campo_correcto(nick, nickfb);
    }

    if (pass_re.val() != "" && pass.val() != "") {
        if (pass_re.val() === pass.val()) {
            campo_correcto(pass, passfb);
            campo_correcto(pass_re, pass_refb);
        } else {
            campo_incorrecto(pass_re, pass_refb, "Las contraseñas no coinciden");
        }
    }
}

function checkpass() {
    checkstart();

    if (old.val() != "") {
        campo_correcto(old, oldfb);
    }

    if (new_re.val() != "" && new_.val() != "") {
        if (new_re.val() === new_.val()) {
            campo_correcto(new_, new_fb);
            campo_correcto(new_re, new_refb);
        } else {
            campo_incorrecto(new_re, new_refb, "Las contraseñas no coinciden");
        }
    }
}

function checkbed() {
    checkstart();

    if (!checkip(ip.val())) {
        campo_incorrecto(ip, ipfb, "La ip no es correcta, ha de estar entre 224.0.0.0 y 239.255.255.255");
    } else if (ip.val() != "") {
        campo_correcto(ip, ipfb);
    }

    if (bedname.val() != "") {
        campo_correcto(bedname, bednamefb)
    }

    if (port.val() != "") {
        campo_correcto(port, portfb)
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
        campo_incorrecto(muid, fb, "El formato no es correcto, ha de ser: AABBCCDDEEFF");
    } else if (muid.val() != "") {
        campo_correcto(muid, fb);
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
    let fun = undefined;
    if (opt === "bed") {
        fun = checkbed;
    } else if (opt === "user") {
        fun = checkuser;
    } else if (opt === "usermod") {
        fun = checkpass;
    }
    fields.forEach(function (element) {
        element.keyup(fun)
    });

});
