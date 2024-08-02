$(document).ready(function() {

    /* =================================================================
        Default Table
    ================================================================= */

    $('#table-1').DataTable();
      
    /* =================================================================
       Exporting Table Data
    ================================================================= */

    $('#table-2').DataTable( {
        dom: 'Bfrtip',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    } );

    /* =================================================================
       Table with Column Filtering
    ================================================================= */

    var $table3 = jQuery("#table3");
    
    var table3 = $table3.DataTable( {
        "aLengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        dom: '<"row"<"col-md-3"l><"col-md-6"B><"col-md-3"fr>><"row"<"col-md-12"t>><"row"<"col-md-5"i><"col-md-7"p>>',
        buttons: [
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5'
        ]
    } );
    
    // Setup - add a text input to each footer cell
    // $( '#table3 tfoot th' ).each( function () {
    //     var title = $('#table3 thead th.search_th').eq( $(this).index() ).text();
    //     $(this).html( '<input type="text" class="form-control" placeholder="Search ' + title + '" />' );
    // } );

    // $('#table3 thead tr').clone(true).appendTo( '#table3 thead' );
    $('#table3 thead.thread_search th').each(function (i){
        var title = $(this).text();
        $(this).html('<input type="text" class="form-control" placeholder="Tìm ' + title + '" />');
        $( 'input', this ).on( 'keyup change', function () {
            if ( table3.column(i).search() !== this.value ) {
                table3.column(i).search( this.value ).draw();
            }
        } );
    });

});