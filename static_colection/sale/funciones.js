let tblProductos;

function formatRepo(repo) {
    if (repo.loading) {
        return repo.text;
    }

    var option = $(
        '<div class="wrapper container">' +
        '<div class="row">' +
        '<div class="col-lg-1">' +
        '<img src="' + repo.image + '" class="img-fluid img-thumbnail d-block mx-auto rounded">' +
        '</div>' +
        '<div class="col-lg-11 text-left shadow-sm">' +
        //'<br>' +
        '<p style="margin-bottom: 0;">' +
        '<b>Nombre:</b> ' + repo.name + '<br>' +
        '<b>Categoría:</b> ' + repo.cat.name + '<br>' +
        '<b>PVP:</b> <span class="badge badge-warning">$' + repo.pvp + '</span>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '</div>');

    return option;
}

var vents = {
    items:{
        cli:'',
        date_joined:'',
        subtotal:0.00,
        iva:0.00,
        total:0.00,
        products:[]
    },
    calculate_invoice: function(){
        var subtotal = 0.00;
        var iva = $('input[name="iva"]').val();
        $.each(this.items.products, function (pos, dict) {
            console.log(pos, dict)
            dict.subtotal = dict.cant * parseFloat(dict.pvp)
            subtotal+=dict.subtotal
        });
        this.items.subtotal=subtotal;
        this.items.iva=this.items.subtotal*iva;
        this.items.total=this.items.subtotal+this.items.iva;

        $('input[name="subtotal"]').val(this.items.subtotal.toFixed(2))
        $('input[name="ivaCalculado"]').val(this.items.iva.toFixed(2))
        $('input[name="total"]').val(this.items.total.toFixed(2))
    },
    add: function (item) {
        this.items.products.push(item);
        this.list();
    },
    list: function () {
        this.calculate_invoice();
       tblProductos = $('#tblProductos').DataTable({
            autoWidth: true,
            destroy:true,
            data: this.items.products,
            columns: [
                {"data":"id"},
                {"data":"name"},
                {"data":"cat.name"},
                {"data":"pvp"},
                {"data":"cant"},
                {"data":"subtotal"},
            ],
            columnDefs:[
                {
                    targets:[0],
                    class:'text-center',
                    orderable: false,
                    render: function (data,type,row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat"><i class="fas fa-trash"></i></a>'
                    }
                },
                {
                    targets:[-3, -1],
                    class:'text-center',
                    orderable: false,
                    render: function (data,type,row) {
                        return '$' + parseFloat(data).toFixed(2)
                    }
                },
                {
                    targets:[-2],
                    class:'text-center',
                    orderable: false,
                    render: function (data,type,row) {
                        return '<input type="text" name="cant" class="form-control form-control" autocomplete="off" value="'+row.cant+'">';
                    }
                },
            ],
            rowCallback(row,data,displayNum,displayIndex,dataIndex){
              $(row).find('input[name="cant"]').TouchSpin({
                  min:1,
                  max:100000,
                  step:1
              })
            },
            initComplete:function (settings, json) {

            }
        })
    }
};

$(document).ready(function () {
    $('input[name="iva"]').TouchSpin({
        min:0,
        max:100,
        step:0.1,
        decimals:2,
        boostat:5,
        maxboostedstep:10,
        postfix:'%'
    }).on('change', function () {
        vents.calculate_invoice();
    }).val(0.12);

    $('#date_joined').datetimepicker({
        format: 'YYYY-MM-DD',
        date:moment().format("YYYY-MM-DD"),
        locale:'es',
        minDate:moment().format("YYYY-MM-DD"),
    });
    $('.select2').select2({
        theme:"bootstrap4",
        languaje:'es'
    });

    // $('input[name="search"]').autocomplete({
    //     source: function (request,response) {
    //       $.ajax({
    //           url:window.location.pathname,
    //           type:'POST',
    //           data:{
    //               'action':'search_products',
    //               'term':request.term
    //           },
    //           dataType:'json'
    //       }).done(function (data) {
    //           response(data)
    //       }).fail(function (jqXHR,textStatus,errorThrown) {
    //           alert(textStatus+' : '+errorThrown)
    //       })
    //
    //     },
    //     delay:500,
    //     minLength:1,
    //     select:function (event,ui) {
    //         event.preventDefault();
    //         console.log(ui.item);
    //         console.clear();
    //         ui.item.cant=1;
    //         ui.item.subtotal=0.00;
    //         console.log(vents.items);
    //         vents.add(ui.item);
    //         $(this).val('')
    //     }
    // })

    $('select[name="search"]').select2({
        theme:'bootstrap4',
        language: 'es',
        allowClear:true,
        ajax:{
            delay:250,
            type:'POST',
            url:window.location.pathname,
            data: function (params) {
                let queryParameters={
                    term:params.term,
                    action:'search_products'
                }
                return queryParameters
            },
            processResults:function (data) {
                return{results:data}
            }
        },
        placeholder:'Ingrese una descripcion',
        minimumInputLength:1,
        templateResult: formatRepo,
    }).on('select2:select', function (e) {
        var data = e.params.data;
        data.cant = 1;
        data.subtotal = 0.00;
        vents.add(data);
        $(this).val('').trigger('change.select2');
    });

    $('#tblProductos tbody').on('change', 'input[name="cant"]', function () {
    let cant = parseInt($(this).val());
    let tr = tblProductos.cell($(this).closest('td, li')).index();
    vents.items.products[tr.row].cant = cant;
    vents.calculate_invoice()
    $('td:eq(5)', tblProductos.row(tr.row).node()).html('$'+vents.items.products[tr.row].subtotal.toFixed(2))
}).on('click', 'a[rel="remove"]', function () {
    let tr = tblProductos.cell($(this).closest('td, li')).index();
    alert_action('Notificacion', 'Estas seguro de eliminar el producto de tu detalle?', function () {
            vents.items.products.splice(tr.row,1)
            vents.list()
        })
    })

    $('.btnRemoveAll').on('click', function () {
        if (vents.items.products.length===0){return false};
        alert_action('Notificacion', 'Estas seguro de eliminar todos los productos de tu detalle?', function () {
            vents.items.products = [];
            vents.list()
        })
    });

    $('.btnClearSearch').on('click', function () {
        $('input[name="search"]').val().focus()
    });

    $('form').on('submit', function (e) {
        e.preventDefault();
        if (vents.items.products.length===0){
            message_error('Debe tener al menos un producto en su venta');
            return false
        }
        vents.items.date_joined= $('input[name="date_joined"]').val();
        vents.items.cli= $('select[name="cli"]').val();
        let parameters = new FormData();
        parameters.append('action', $('input[name="action"]').val());
        parameters.append('vents', JSON.stringify(vents.items));
        submit_with_ajax(window.location.pathname,'Notificacion', 'Estas seguro de realizar la accion', parameters,
            function () {
            let url = '/erp/dashboard/';
            location.href = url
        })
    })
    vents.list()

});

