    function SeleccionarCategoria(){
        var cantidad = $('#numElement').val();

        var str = $('#searchString').val();
        var res = str.split(" ");

        var message = JSON.stringify({
                "values": res,
                "cantidad": cantidad
            });

        $.ajax({
            url:'/consulta',
            type:'POST',
            contentType: 'application/json',
            data : message,
            dataType:'json',
            success: function(response){
                },
            error: function(response){
                if(response['status']==401){
                    }
                 else{
                  }}
        });
    }
