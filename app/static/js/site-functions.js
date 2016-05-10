// *************************************************************************
// Copyright (c) 2016 Cisco Systems, Inc.  All rights reserved.
// *************************************************************************


function create_group(){
    $('#create_group_name').rules("add", "required");
    if($('#network_form').valid()){
        $('#operation').val('create_group')
        submit_form('group_handler')
        $('#create_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_group_name').rules("remove", "required");
}

function get_groups(){
    $('#operation').val('get_groups')
    submit_form('group_handler')
    $('#create_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function get_tenants(){
    $('#operation').val('tenant_list');
    submit_form('group_handler')
    $('#tenant_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function delete_group() {
    $('#sel_delete_group_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('delete_group')
            submit_form('group_handler')
            $('#delete_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_group_name').rules("remove", "required");
}

function get_network_list(){
    $('#operation').val('get_network_list');
    submit_form('network_handler')
    $('#network_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function create_network(){
    $('#create_network_name').rules("add", "required");
    $('#create_network_encapsulation').rules("add", "required");
    $('#sel_create_network_group').rules("add", "required");
    if($('#network_form').valid()){
        $('#operation').val('create_network')
        submit_form('network_handler')
        $('#create_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_network_name').rules("remove", "required");
    $('#create_network_encapsulation').rules("remove", "required");
    $('#sel_create_network_group').rules("remove", "required");
}


function get_sel_delete_networks() {
    $('#sel_delete_network_group').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_sel_delete_networks')
            submit_form('network_handler')
            $('#delete_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_group').rules("remove", "required");
}

function delete_network() {
    $('#sel_delete_network_group').rules("add", "required");
    $('#sel_delete_network_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('delete_network')
            submit_form('network_handler')
            $('#delete_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_name').rules("remove", "required");
    $('#sel_delete_network_group').rules("remove", "required");
}

function submit_network_form() {
    if($('#network_form').valid()){
        Sijax.request('network_form_handler', [Sijax.getFormValues('#network_form')]);
    }
}

function submit_form(handler_name) {
    if($('#network_form').valid()){
        Sijax.request(handler_name, [Sijax.getFormValues('#network_form')]);
    }
}


function get_leafs(){
    if($('#network_form').valid()){
            $('#operation').val('get_leafs')
            submit_form('fabric_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

function get_ports(){
    $('#sel_leaf_create_vpc').rules("add", "required");
    $('#sel_port_create_vpc').html("");
    if($('#network_form').valid()){
            $('#operation').val('get_ports')
            submit_form('fabric_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_leaf_create_vpc').rules("remove", "required");
}

function add_port(){
    $('#create_vpc_response').html('')
    $('#sel_port_create_vpc').rules("add", "required");
    $('#sel_leaf_create_vpc').rules("add", "required");
    if($('#network_form').valid()){
        add_to_list = true;
        // Check if port has been added and if there is no more than two switches selected
        var switch_selection = $('#sel_leaf_create_vpc option:selected').text()
        var switch_selected_list = []
        $("#vpc_ports tr").each(function(index) {
            if (index != 0) {

                $row = $(this);

                var id = $row.find("td:first").text();

                if (id.indexOf($('#sel_port_create_vpc').val()) == 0) {
                       $('#create_vpc_response').html(
                       '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Port already added</label>'
                       );
                       add_to_list = false;
                       return;
                }
            }
        });
        if (add_to_list){
            tr_id = ($('#sel_leaf_create_vpc option:selected').text() + $('#sel_port_create_vpc option:selected').text()).
            replace('-','').replace('/','');
            $('#vpc_ports > tbody > tr').eq(0).after(
                '<tr id=' +
                tr_id +
                '><td style="display:none">' +
                $('#sel_port_create_vpc').val() +
                '</td><td>' + $('#sel_leaf_create_vpc option:selected').text() +
                '</td><td>' + $('#sel_port_create_vpc option:selected').text() +
                '</td><td><i class="fa fa-times-circle" onclick="$(\'#' +
                tr_id +
                '\').remove();"></i>' +
                '</td></tr>'
            );
        }
    }
    $('#sel_port_create_vpc').rules("remove", "required");
    $('#sel_leaf_create_vpc').rules("remove", "required");
}

function get_vpc_list(){
    $('#operation').val('get_vpc_list');
    submit_form('vpc_handler')
    $('#vpc_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function create_vpc(){
    switch_selected_list = []
    $("#vpc_ports tr").each(function(index) {
            if (index != 0) {
                $row = $(this);
                var switch_id = $row.find("td:nth-child(2)").text()
                var is_selected = false;
                if (switch_id != '') {
                    for (i = 0; i < switch_selected_list.length; i++) {
                        if (switch_selected_list[i] === switch_id){
                            is_selected = true;
                        }
                    }

                    if (!is_selected){
                        switch_selected_list.push(switch_id)
                    }
                }
            }
        });
    if($("#vpc_ports tr").length - 3 <= 0){
        $('#create_vpc_response').html(
                   '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Must assign at least two ports</label>'
                   );
        return;
    }
    if(switch_selected_list.length != 2){
         $('#create_vpc_response').html(
                   '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Must assign exactly two different switches</label>'
                   );
        return;
    }
    port_dns = ''
    $("#vpc_ports tr").each(function(index) {
            if (index != 0) {
                $row = $(this);
                port_dns += $row.find("td:first").text() + ";";
            }
        });
    $('#port_dns').val(port_dns);
    $('#create_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('create_vpc')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_vpc_name').rules("remove", "required");
}



function get_delete_vpc_assigned_ports(){
    $('#sel_delete_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#delete_vpc_ports').html('')
            $('#operation').val('get_delete_vpc_assigned_ports')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_vpc_name').rules("remove", "required");
}

function get_vpcs(){
    if($('#network_form').valid()){
            $('#operation').val('get_vpcs')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

function delete_vpc(){
    $('#sel_delete_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('delete_vpc')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_vpc_name').rules("remove", "required");
}

function get_create_vpc_access_networks() {
    $('#sel_group_create_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_create_vpc_access_networks')
            submit_form('vpc_access_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_create_vpc_access').rules("remove", "required");
}

function get_vpc_assignment_list(){
    $('#operation').val('get_vpc_assignment_list');
    submit_form('vpc_access_handler')
    $('#vpc_assignment_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function create_vpc_access(){
    $('#sel_group_create_vpc_access').rules("add", "required");
    $('#sel_network_create_vpc_access').rules("add", "required");
    $('#sel_vpc_create_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('create_vpc_access')
            submit_form('vpc_access_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_create_vpc_access').rules("remove", "required");
    $('#sel_network_create_vpc_access').rules("remove", "required");
    $('#sel_vpc_create_vpc_access').rules("remove", "required");
}

function get_delete_vpc_access_networks(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_delete_vpc_access_networks')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
}

function get_delete_vpc_access_assignments(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    $('#sel_network_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_delete_vpc_access_assignments')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
    $('#sel_network_delete_vpc_access').rules("remove", "required");
}

function delete_network_vpc_assignments(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    $('#sel_network_delete_vpc_access').rules("add", "required");
    $('#sel_vpc_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('delete_vpc_access')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
    $('#sel_network_delete_vpc_access').rules("remove", "required");
    $('#sel_vpc_delete_vpc_access').rules("remove", "required");
}

function get_create_single_access_networks() {
    $('#sel_create_single_access_group').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_create_single_access_networks')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_group').rules("remove", "required");
}
function get_create_single_access_ports () {
    $('#sel_create_single_access_leaf').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_create_single_access_ports')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_leaf').rules("remove", "required");
}
function create_single_access(){
    $('#sel_create_single_access_leaf').rules("add", "required");
    $('#sel_create_single_access_group').rules("add", "required");
    $('#sel_create_single_access_network').rules("add", "required");
    $('#sel_create_single_access_port').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('create_single_access')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_port').rules("remove", "required");
    $('#sel_create_single_access_network').rules("remove", "required");
    $('#sel_create_single_access_group').rules("remove", "required");
    $('#sel_create_single_access_leaf').rules("remove", "required");
}

function get_delete_single_access_networks() {
    $('#sel_delete_single_access_group').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_delete_single_access_networks')
            submit_form('single_access_handler')
            $('#delete_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_single_access_group').rules("remove", "required");
}
function get_delete_single_access_ports () {
    $('#sel_delete_single_access_leaf').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('get_delete_single_access_ports')
            submit_form('single_access_handler')
            $('#delete_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_single_access_leaf').rules("remove", "required");
}
function delete_single_access(){
    $('#sel_delete_single_access_leaf').rules("add", "required");
    $('#sel_delete_single_access_group').rules("add", "required");
    $('#sel_delete_single_access_network').rules("add", "required");
    $('#sel_delete_single_access_port').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('delete_single_access')
            submit_form('single_access_handler')
            $('#delete_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_single_access_port').rules("remove", "required");
    $('#sel_delete_single_access_network').rules("remove", "required");
    $('#sel_delete_single_access_group').rules("remove", "required");
    $('#sel_delete_single_access_leaf').rules("remove", "required");
}

function get_create_network_profile_networks(){
    $('#sel_create_network_profile_group').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('get_create_network_profile_networks')
            submit_form('network_handler')
            $('#create_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_network_profile_group').rules('remove','required')
}

function add_create_network_profile(){
    $('#create_network_profile_response').html('')
    $('#sel_create_network_profile_group').rules("add", "required");
    $('#sel_create_network_profile_network').rules("add", "required");
    if($('#network_form').valid()){
        tr_id = $('#sel_create_network_profile_network option:selected').val().replace(/-/g,'').replace(/\//g,'')
        is_added = false;
        $("#table_create_network_profile tr").each(function(index) {
            if (index != 0) {

                $row = $(this);

                var id = $row.find("td:first").text().replace(/-/g,'').replace(/\//g,'');

                if (id.indexOf(tr_id) == 0) {
                       $('#create_network_profile_response').html(
                       '<label class="label label-danger" > <i class="fa fa-times-circle"></i> VLAN already added</label>'
                       );
                       is_added = true;
                }
            }
        });
        if (!is_added){
            $('#table_create_network_profile > tbody > tr').eq(0).after(
                '<tr id=' +
                tr_id +
                '><td style="display:none">' +
                $('#sel_create_network_profile_network option:selected').val() +
                '</td><td>' + $('#sel_create_network_profile_group option:selected').text() +
                '</td><td>' + $('#sel_create_network_profile_network option:selected').text() +
                '</td><td><i class="fa fa-times-circle" onclick="$(\'#' +
                tr_id +
                '\').remove();"></i>' +
                '</td></tr>'
            );
        }
    }
    $('#sel_create_network_profile_group').rules("remove", "required");
    $('#sel_create_network_profile_network').rules("remove", "required");
}

function create_network_profile(){
    if($("#table_create_network_profile tr").length - 2 <= 0){
        $('#create_network_profile_response').html(
        '<label class="label label-danger" > <i class="fa fa-times-circle">' +
        '</i>You must assign at least two VLANS</label>');
        return;
    }
    network_dns = ''
    $("#table_create_network_profile tr").each(function(index) {
            if (index != 0) {
                $row = $(this);
                network_dns += $row.find("td:first").text() + ";";
            }
        });
    $('#create_network_profile_dns').val(network_dns);
    $('#create_network_profile_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#operation').val('create_network_profile')
            submit_form('network_handler')
            $('#create_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_network_profile_name').rules("remove", "required");

}

function get_network_profile_list(){
    $('#operation').val('get_network_profile_list');
    submit_form('network_handler')
    $('#network_profile_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function get_network_profiles(){
    if($('#network_form').valid()){
            $('#operation').val('get_network_profiles')
            submit_form('network_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

function get_delete_network_profile_networks(){
    $('#sel_delete_network_profile').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('get_delete_network_profile_networks')
            submit_form('network_handler')
            $('#delete_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_profile').rules('remove','required')
}

function delete_network_profile(){
    $('#sel_delete_network_profile').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('delete_network_profile')
            submit_form('network_handler')
            $('#delete_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_profile').rules('remove','required')
}

function create_access_switch(){
    $('#access_switch_hostname').rules('add','required')
    $('#access_switch_ip').rules('add','required')
    $('#access_switch_user').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('create_access_switch')
            submit_form('access_switch_handler')
            $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#access_switch_hostname').rules('remove','required')
    $('#access_switch_ip').rules('remove','required')
    $('#access_switch_user').rules('remove','required')
}

function get_access_switch_list(){
    $('#operation').val('get_access_switch_list');
    submit_form('access_switch_handler');
    $('#access_switch_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function configure_access_switches(){
    if ($("#table_access_switches tr").length < 3){
        $('#access_switch_response').html(
            '<label class="label label-danger">' +
            '<i class="fa fa-times-circle"></i> You must add at least one switch</label>'
        );
        return;
    }
    $('#access_switch_login_password').rules('add','required')
    $('#access_switch_enable_password').rules('add','required')
    $('#access_switch_commands').rules('add','required')
    if($('#network_form').valid()){
        switches_info = '';
        $("#table_access_switches tr").each(function(index) {
            if (index != 0) {
                $row = $(this);
                switches_info += $row.find("td:first").text() + ";";
            }
        });
        $('#hd_configure_access_switches').val(switches_info)
        $('#operation').val('configure_access_switches')
        submit_form('access_switch_handler')
        $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#access_switch_login_password').rules('remove','required')
    $('#access_switch_enable_password').rules('remove','required')
    $('#access_switch_commands').rules('remove','required')
}

function get_access_switches(){
    if($('#network_form').valid()){
            $('#operation').val('get_access_switches')
            submit_form('access_switch_handler')
            $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

function delete_access_switch(){
    $('#sel_delete_access_switch').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('delete_access_switch')
            submit_form('access_switch_handler')
            $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_access_switch').rules('remove','required')
}

function add_switch(){
    $('#access_switch_response').html('')
    $('#sel_access_switch').rules("add", "required");
    if($('#network_form').valid()){
        add_to_list = true;
        // Check if switch has been added
        var switch_selected_list = []
        $("#table_access_switches tr").each(function(index) {
            if (index != 0) {

                $row = $(this);

                var id = $row.find("td:first").text();

                if (id.indexOf($('#sel_access_switch').val()) == 0) {
                       $('#access_switch_response').html(
                       '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Switch already added</label>'
                       );
                       add_to_list = false;
                       return;
                }
            }
        });
        if (add_to_list){
            tr_id = $('#sel_access_switch').val().replace(/\./g,'')
            $('#table_access_switches > tbody > tr').eq(0).after(
                '<tr id=' +
                tr_id +
                '><td>' +
                $('#sel_access_switch option:selected').text() +
                '</td><td><i class="fa fa-times-circle" onclick="$(\'#' +
                tr_id +
                '\').remove();"></i>' +
                '</td></tr>'
            );
        }
    }
    $('#sel_access_switch').rules("remove", "required");
}

function create_vpc_group() {
    if ($('#sel_create_vpc_group_leaf_1').val() == $('#sel_create_vpc_group_leaf_2').val()) {
        $('#div_create_vpc_group_response').html(
        '<label class="label label-danger" > <i class="fa fa-times-circle">' +
        '</i>You must choose two different leaf switches</label>');
        return;
    }
    $('#sel_create_vpc_group_leaf_1').rules('add','required')
    $('#sel_create_vpc_group_leaf_2').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('create_vpc_group')
            submit_form('vpc_handler')
            $('#div_create_vpc_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_vpc_group_leaf_1').rules('remove','required')
    $('#sel_create_vpc_group_leaf_2').rules('remove','required')
}

function get_vpc_group_list(){
    $('#operation').val('get_vpc_group_list');
    submit_form('vpc_handler')
    $('#vpc_group_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

function get_vpc_groups(){
    if($('#network_form').valid()){
            $('#operation').val('get_vpc_groups')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

function get_leafs_by_vpc_group() {
    $('#sel_vpc_group_create_vpc').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('get_leafs_by_vpc_group')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_vpc_group_create_vpc').rules('remove','required')
}

function delete_vpc_group(){
    $('#sel_delete_vpc_group_name').rules('add','required')
    if($('#network_form').valid()){
            $('#operation').val('delete_vpc_group')
            submit_form('vpc_handler')
            $('#delete_vpc_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_vpc_group_name').rules('remove','required')
}

function create_notification(title, message, type, delay) {
    $.notify({
        // options
        title: '<strong>' + title + '</strong>',
        message: '<p>' + message + '</p>'
    },{
        // settings
        type: type,
        placement: {
            from: "top",
            align: "right"
        },
        animate: {
            enter: 'animated fadeInRight',
            exit: 'animated fadeOutRight'
        },
        delay: delay,
        template: '<div data-notify="container" class="col-xs-11 col-sm-2 alert alert-{0}" role="alert">' +
            '<button type="button" aria-hidden="true" class="close" data-notify="dismiss">×</button>' +
            '<span data-notify="icon"></span> ' +
            '<span data-notify="title">{1}</span> ' +
            '<span data-notify="message">{2}</span>' +
            '<div class="progress" data-notify="progressbar">' +
                '<div class="progress-bar progress-bar-{0}" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>' +
            '</div>' +
            '<a href="{3}" target="{4}" data-notify="url"></a>' +
	    '</div>'
    });
}
function clean_inputs(){
    $('select').val('');
    $('input[type=text]').val('');
    $('input[type=password]').val('');
    $('.label-danger').remove();
    $('.error').remove();
    $('tbody').html('<tr></tr>')
}

function get_health_dashboard(){
    if($('#network_form').valid()){
            $('#operation').val('get_health_dashboard')
            submit_form('fabric_handler')
            $('#noc_monitor_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    // Refresh the health scores each 10 seconds
    setTimeout(get_health_dashboard,30000)
}

