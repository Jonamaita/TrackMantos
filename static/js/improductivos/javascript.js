$(document).ready(function() {
    //console.log("jquery On");
    /////Enviar Datos form ///////////
    $("#enviar-form").click(function() {
        validar_form();
    });
    //////////////////////////////////
    $("#btn_falla_resuelta").click(function() {
        hora_falla_resuelta();
    })
    //////////////////////////////////
    $("#checkProduccion").click(function() {
        enable_produccion();
    })
    $("#checkElectrico,#checkMecanico").click(function() {
        enable_produccion();
    })
    /////////////////////////////////
});

function validar_form() {
    var expreg = /\S/;
    var valTextArea = document.getElementById('comentario').value;
    var checkProduccion = $("#checkProduccion").prop('checked');
    if (!valTextArea.match(expreg) && checkProduccion != true) { // Si esta seleccionado el checbox producción no es necesario comentario
        alert("El campo de comentario no puede estar vacio.");
        $("#comentario").focus();
        //$("#comentario").addClass("incorrecto")
        return false;
    } else {
        $.ajax({
            type: "POST",
            url: "/datos_track",
            data: $('#form_1').serialize(),
            success: function(data) {
               // console.log(data);
                if (data != false) {
                    //funcion que se ejecutara en caso de que todo vaya bien
                    //$('#res_form').addClass('correcto');
                    $('#form_success_error').removeClass('no-visible');
                    $('#res_form').text("Los datos se enviaron correctamente.");
                    document.getElementById("form_1").reset();
                    $("#run_tf").removeClass("hide");
                    //document.getElementById("comentario").disabled = true;
                    //document.getElementById("enviar-form").disabled = true;
                    $("#text_comentario").addClass("animated fadeOutUp");
                    $("#enviar-form").addClass("animated fadeOutUp");
                    // console.log(data); // Muestra lo que envia el servidor
                    setTimeout(function() {
                        $("#text_comentario,#form_1").toggle("slow");
                    }, 1000);
                } else {
                    $('#form_success_error').removeClass('no-visible');
                    $('#res_form').text("Los datos no se pudieron escribir correctamente, intente nuevamente.");
                    document.getElementById("form_1").reset();
                }
            },
            error: function(data) {
                //funcion que se ejecutara en caso de que se haya producido un fallo en la petición
                $('#res_form').addClass('incorrecto');
                $('#form_success_error').removeClass('no-visible');
                $('#res_form').text("Los datos no se enviaron correctamente, intente nuevamente.");
                document.getElementById("form_1").reset();
            }
        });
    }
};

function hora_falla_resuelta() {
    $.ajax({
        type: "POST",
        url: "/falla_resuelta",
        success: function(data) {
            //console.log(data);
            if (data == true) {
                $("#div_falla").removeClass("hide");
                $("#falla_resuelta").addClass("correcto").html("Se ha registrado conrrectamente la hora en la que se resolvió la falla. Seras redirigido a la pagina principal.");
                $("#form_success_error,#run_tf,#form_success_errors").toggle("slow");
                setTimeout(function() {
                    location.reload();
                }, 2000);
            } else if(data==false){
                $("#div_falla").removeClass("hide");
                $("#text_comentario,#form_1,#run_tf").toggle("slow");
                $("#falla_resuelta").html("No se ha registrado la hora, posiblemente no se ha registrado una falla. Intente nuevamente.");
                setTimeout(function() {
                    location.reload();

                }, 2000);
            }else{
                alert("Los datos no se pudieron escribir correctamente, intente nuevamente.");
                setTimeout(function() {
                    location.reload();

                }, 100);
                
            }
        },
        error: function() {
            //console.log("Error petición del servidor POST");
           $("#res_falla").addClass("incorrecto").html("Error en la petición al servidor.");
        }
    })
}
////////////////////Habilar opciones de producción/////////////////////
function enable_produccion() {
    if (form_1.checkProduccion.checked) {
        $("#listProduccion").removeClass("hide");
        $("#checkGoteros").prop("checked", true);
        $("#checkGoteros,#checkRuedas,#checkTroquelado,#checkFilm,#checkAjusteMecanico").attr("disabled", false);
    } else {
        $("#listProduccion").addClass("hide");
        $("#checkGoteros,#checkRuedas,#checkTroquelado,#checkFilm,#checkAjusteMecanico").prop("checked", false);
        $("#checkGoteros,#checkRuedas,#checkTroquelado,#checkFilm,#checkAjusteMecanico").attr("disabled", true);
    }
}
/////////////////////////////////////////////