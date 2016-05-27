/*

This file contains all Ajax calls that are made using sijax. All methods have the following structure
- Validation rules are added to when some field is required for the operation
- Check if the required fields are valid
- If valid, perform the operation sending an Ajax request to the server and show the loading gif
- Remove validation rules to required fields
*/

function submit_network_form() {
    if($('#network_form').valid()){
        Sijax.request('network_form_handler', [Sijax.getFormValues('#network_form')]);
    }
}

/**
 * Submit the network_form using Sijax
 */
function submit_form(handler_name) {
    if($('#network_form').valid()){
        Sijax.request(handler_name, [Sijax.getFormValues('#network_form')]);
    }
}

/**
 * Makes a call to the group handler and set the operation to create_group.
 * If successfully, will create a tenant in ACI
 */
function create_group(){
    // Add rules
    $('#create_group_name').rules("add", "required");
    // Check rules
    if($('#network_form').valid()){
        Sijax.request('create_group', [Sijax.getFormValues('#network_form')]);
        //Show loading gif
        $('#create_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    // Remove rules
    $('#create_group_name').rules("remove", "required");
}

/**
 * Makes a call to the group handler and set the operation to get_groups.
 * If successfully, will populate all group selects
 */
function get_groups(){
    Sijax.request('get_groups');
    $('#create_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

/**
 * Makes a call to the group handler and set the operation to tenant_list.
 * If successfully, will populate the group list
 */
function get_tenants(){
    Sijax.request('tenant_list');
    $('#tenant_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

/**
 * Makes a call to the group handler and set the operation to delete_group.
 * If successfully, will delete a tenant.
 */
function delete_group() {
    $('#sel_delete_group_name').rules("add", "required");
    if($('#network_form').valid()){
            Sijax.request('delete_group', [Sijax.getFormValues('#network_form')]);
            $('#delete_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_group_name').rules("remove", "required");
}

/**
 * Makes a call to the network handler and set the operation to get_network_list.
 * If successfully, will populate the network list
 */
function get_network_list(){
    $('#operation').val('get_network_list');
    submit_form('network_handler')
    $('#network_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

/**
 * Makes a call to the network handler and set the operation to create_network.
 * If successfully, will create a VLAN
 */
function create_network(){
    $('#create_network_name').rules("add", "required");
    $('#create_network_encapsulation').rules("add", "required");
    $('#sel_create_network_group').rules("add", "required");
    if($('#network_form').valid()){
        //Set operation hidden input value
        $('#operation').val('create_network')
        submit_form('network_handler')
        $('#create_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_network_name').rules("remove", "required");
    $('#create_network_encapsulation').rules("remove", "required");
    $('#sel_create_network_group').rules("remove", "required");
}


/**
 * Makes a call to the network handler and set the operation to get_sel_delete_networks.
 * If successfully, will populate the get_sel_delete_networks select with all networks within the selected group
 */
function get_sel_delete_networks() {
    $('#sel_delete_network_group').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_sel_delete_networks')
            submit_form('network_handler')
            $('#delete_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_group').rules("remove", "required");
}

/**
 * Makes a call to the network handler and set the operation to delete_network.
 * If successfully, will remove a VLAN
 */
function delete_network() {
    $('#sel_delete_network_group').rules("add", "required");
    $('#sel_delete_network_name').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('delete_network')
            submit_form('network_handler')
            $('#delete_network_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_name').rules("remove", "required");
    $('#sel_delete_network_group').rules("remove", "required");
}

/**
 * Makes a call to the fabric handler and set the operation to get_leafs.
 * If successfully, will populate all leaf selects
 */
function get_leafs(){
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_leafs')
            submit_form('fabric_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

/**
 * Makes a call to the fabric handler and set the operation to get_ports.
 * If successfully, will populate the sel_port_create_vpc select with the ports of the selected leaf
 */
function get_ports(){
    $('#sel_leaf_create_vpc').rules("add", "required");
    $('#sel_port_create_vpc').html("");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_ports')
            submit_form('fabric_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_leaf_create_vpc').rules("remove", "required");
}

/**
 * Add a row to the table vpc_ports checking first if the selected port and selected switch has been selected before
 */
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

/**
 * Makes a call to the vpc handler and set the operation to get_vpc_list.
 * If successfully, will populate the virtual port channel list with the ports that are part of the vpc
 */
function get_vpc_list(){
    //Set operation hidden input value
    $('#operation').val('get_vpc_list');
    submit_form('vpc_handler')
    $('#vpc_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

/**
 * Makes a call to the vpc handler and set the operation to create_vpc.
 * If successfully, will create a vpc
 */
function create_vpc(){
    //Declare a list where the selected switches will be stored
    switch_selected_list = []
    //Traverse the vpc_port table checking that there is not the same port for the same switch two times
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
    //Check that at least two ports have been selected
    if($("#vpc_ports tr").length - 3 <= 0){
        $('#create_vpc_response').html(
                   '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Must assign at least two ports</label>'
                   );
        return;
    }
    //Check if there is more or less than two switches selected
    if(switch_selected_list.length != 2){
         $('#create_vpc_response').html(
                   '<label class="label label-danger" > <i class="fa fa-times-circle"></i> Must assign exactly two different switches</label>'
                   );
        return;
    }
    //Variable to store the selected ports distinguished names
    port_dns = ''
    //All selected ports distinguished name is saved in the port_dns variable separated by a ';' character
    $("#vpc_ports tr").each(function(index) {
            if (index != 0) {
                $row = $(this);
                port_dns += $row.find("td:first").text() + ";";
            }
        });
    //Set a hidden with the port_dns value to be able to submit that information to the server
    $('#port_dns').val(port_dns);
    $('#create_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('create_vpc')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_vpc_name').rules("remove", "required");
}

/**
 * Makes a call to the vpc handler and set the operation to get_delete_vpc_assigned_ports.
 * If successfully, will populate the delete_vpc_ports table with the ports that are
 * bundled in the selected vpc
 */
function get_delete_vpc_assigned_ports(){
    $('#sel_delete_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            $('#delete_vpc_ports').html('')
            //Set operation hidden input value
            $('#operation').val('get_delete_vpc_assigned_ports')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_vpc_name').rules("remove", "required");
}

/**
 * Makes a call to the vpc handler and set the operation to get_vpcs.
 * If successfully, will populate all vpc selects
 */
function get_vpcs(){
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_vpcs')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}

/**
 * Makes a call to the vpc handler and set the operation to delete_vpc.
 * If successfully, will remove a virtual port channel
 */
function delete_vpc(){
    $('#sel_delete_vpc_name').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('delete_vpc')
            submit_form('vpc_handler')
            $('#delete_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_vpc_name').rules("remove", "required");
}

/**
 * Makes a call to the vpc access handler and set the operation to get_create_vpc_access_networks.
 * If successfully, will populate the sel_network_create_vpc_access with the networks within the selected group
 */
function get_create_vpc_access_networks() {
    $('#sel_group_create_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_create_vpc_access_networks')
            submit_form('vpc_access_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_create_vpc_access').rules("remove", "required");
}

/**
 * Makes a call to the vpc access handler and set the operation to get_vpc_assignment_list.
 * If successfully, will populate the vpc assignment list
 */
function get_vpc_assignment_list(){
    //Set operation hidden input value
    $('#operation').val('get_vpc_assignment_list');
    submit_form('vpc_access_handler')
    $('#vpc_assignment_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}

/**
 * Makes a call to the vpc access handler and set the operation to create_vpc_access.
 * If successfully, will create allow the selected VLAN to go through the virtual port channel
 */
function create_vpc_access(){
    $('#sel_group_create_vpc_access').rules("add", "required");
    $('#sel_network_create_vpc_access').rules("add", "required");
    $('#sel_vpc_create_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('create_vpc_access')
            submit_form('vpc_access_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_create_vpc_access').rules("remove", "required");
    $('#sel_network_create_vpc_access').rules("remove", "required");
    $('#sel_vpc_create_vpc_access').rules("remove", "required");
}

/**
 * Makes a call to the vpc access handler and set the operation to get_delete_vpc_access_networks.
 * If successfully, will populate the sel_network_delete_vpc_access select with the networks within the selected
 * group
 */
function get_delete_vpc_access_networks(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_delete_vpc_access_networks')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
}

/**
 * Makes a call to the vpc access handler and set the operation to get_delete_vpc_access_assignments.
 * If successfully, will populate the sel_vpc_delete_vpc_access with the networks that are allowed to go through
 * the selected virtual port channel
 */
function get_delete_vpc_access_assignments(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    $('#sel_network_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_delete_vpc_access_assignments')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
    $('#sel_network_delete_vpc_access').rules("remove", "required");
}

/**
 * Makes a call to the vpc access handler and set the operation to delete_vpc_access.
 * If successfully, will deny the selected network to go through the virtual port channel
 */
function delete_network_vpc_assignments(){
    $('#sel_group_delete_vpc_access').rules("add", "required");
    $('#sel_network_delete_vpc_access').rules("add", "required");
    $('#sel_vpc_delete_vpc_access').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('delete_vpc_access')
            submit_form('vpc_access_handler')
            $('#div_delete_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_group_delete_vpc_access').rules("remove", "required");
    $('#sel_network_delete_vpc_access').rules("remove", "required");
    $('#sel_vpc_delete_vpc_access').rules("remove", "required");
}

/**
 * Makes a call to the single access handler and set the operation to get_create_single_access_networks.
 * If successfully, will populate the sel_create_single_access_network select with the networks within the selected
 * group
 */
function get_create_single_access_networks() {
    $('#sel_create_single_access_group').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_create_single_access_networks')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_group').rules("remove", "required");
}

/**
 * Makes a call to the single access handler and set the operation to get_create_single_access_ports.
 * If successfully, will populate the sel_create_single_access_leaf select with the available ports of the
 * selected leaf
 */
function get_create_single_access_ports () {
    $('#sel_create_single_access_leaf').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_create_single_access_ports')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_leaf').rules("remove", "required");
}

/**
 * Makes a call to the single access handler and set the operation to create_single_access.
 * If successfully, will allow the selected VLAN to go through the selected port
 */
function create_single_access(){
    $('#sel_create_single_access_leaf').rules("add", "required");
    $('#sel_create_single_access_group').rules("add", "required");
    $('#sel_create_single_access_network').rules("add", "required");
    $('#sel_create_single_access_port').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('create_single_access')
            submit_form('single_access_handler')
            $('#create_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_single_access_port').rules("remove", "required");
    $('#sel_create_single_access_network').rules("remove", "required");
    $('#sel_create_single_access_group').rules("remove", "required");
    $('#sel_create_single_access_leaf').rules("remove", "required");
}

/**
 * Makes a call to the single access handler and set the operation to get_delete_single_access_networks.
 * If successfully, will populate the sel_delete_single_access_network with the networks within the selected
 * group
 */
function get_delete_single_access_networks() {
    $('#sel_delete_single_access_group').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_delete_single_access_networks')
            submit_form('single_access_handler')
            $('#delete_single_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_single_access_group').rules("remove", "required");
}

/**
 * Makes a call to the single access handler and set the operation to get_delete_single_access_ports.
 * If successfully, will populate all group selects
 */
function get_delete_single_access_ports () {
    $('#sel_delete_single_access_leaf').rules("add", "required");
    if($('#network_form').valid()){
            //Set operation hidden input value
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
            //Set operation hidden input value
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
            //Set operation hidden input value
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
            //Set operation hidden input value
            $('#operation').val('create_network_profile')
            submit_form('network_handler')
            $('#create_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#create_network_profile_name').rules("remove", "required");

}


function get_network_profile_list(){
    //Set operation hidden input value
    $('#operation').val('get_network_profile_list');
    submit_form('network_handler')
    $('#network_profile_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}


function get_network_profiles(){
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_network_profiles')
            submit_form('network_handler')
            $('#div_create_vpc_access_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}


function get_delete_network_profile_networks(){
    $('#sel_delete_network_profile').rules('add','required')
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_delete_network_profile_networks')
            submit_form('network_handler')
            $('#delete_network_profile_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_delete_network_profile').rules('remove','required')
}


function delete_network_profile(){
    $('#sel_delete_network_profile').rules('add','required')
    if($('#network_form').valid()){
            //Set operation hidden input value
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
            Sijax.request('create_access_switch', [Sijax.getFormValues('#network_form')]);
            $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#access_switch_hostname').rules('remove','required')
    $('#access_switch_ip').rules('remove','required')
    $('#access_switch_user').rules('remove','required')
}


function get_access_switch_list(){
    Sijax.request('get_access_switch_list');
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
        //Set operation hidden input value
        Sijax.request('configure_access_switches', [Sijax.getFormValues('#network_form')]);
        $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#access_switch_login_password').rules('remove','required')
    $('#access_switch_enable_password').rules('remove','required')
    $('#access_switch_commands').rules('remove','required')
}


function get_access_switches(){
    Sijax.request('get_access_switches');
    $('#access_switch_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
}


function delete_access_switch(){
    $('#sel_delete_access_switch').rules('add','required')
    if($('#network_form').valid()){
            Sijax.request('delete_access_switch', [Sijax.getFormValues('#network_form')]);
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
            //Set operation hidden input value
            $('#operation').val('create_vpc_group')
            submit_form('vpc_handler')
            $('#div_create_vpc_group_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_create_vpc_group_leaf_1').rules('remove','required')
    $('#sel_create_vpc_group_leaf_2').rules('remove','required')
}


function get_vpc_group_list(){
    //Set operation hidden input value
    $('#operation').val('get_vpc_group_list');
    submit_form('vpc_handler')
    $('#vpc_group_list').html('<img src="/static/images/loading.gif" style="height:20px" />');
}


function get_vpc_groups(){
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_vpc_groups')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
}


function get_leafs_by_vpc_group() {
    $('#sel_vpc_group_create_vpc').rules('add','required')
    if($('#network_form').valid()){
            //Set operation hidden input value
            $('#operation').val('get_leafs_by_vpc_group')
            submit_form('vpc_handler')
            $('#create_vpc_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    $('#sel_vpc_group_create_vpc').rules('remove','required')
}


function delete_vpc_group(){
    $('#sel_delete_vpc_group_name').rules('add','required')
    if($('#network_form').valid()){
            //Set operation hidden input value
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
            //Set operation hidden input value
            $('#operation').val('get_health_dashboard')
            submit_form('fabric_handler')
            $('#noc_monitor_response').html('<img src="/static/images/loading.gif" style="height:20px" />');
    }
    // Refresh the health scores each 10 seconds
    setTimeout(get_health_dashboard,30000)
}

function netmon_netlist(){
    Sijax.request('network_list');
}

function get_endpoints(){
    Sijax.request('get_endpoints',[Sijax.getFormValues('#network_form')]);
}

function get_epg_health_score(){
    Sijax.request('get_epg_health_score',[Sijax.getFormValues('#network_form')]);
}

function get_faults_history(){
    Sijax.request('get_faults_history',[Sijax.getFormValues('#network_form')]);
}

function load_traffic_chart(lables, data){
    var ctx = document.getElementById("traffic_chart");

    var data = {
        labels: lables,
        datasets: [
            {
                label: "EPG Ingress Unicast Traffic",
                fill: false,
                lineTension: 0.1,
                backgroundColor: "rgba(75,192,192,0.4)",
                borderColor: "rgba(75,192,192,1)",
                borderCapStyle: 'butt',
                borderDash: [],
                borderDashOffset: 0.0,
                borderJoinStyle: 'miter',
                pointBorderColor: "rgba(75,192,192,1)",
                pointBackgroundColor: "#fff",
                pointBorderWidth: 1,
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(75,192,192,1)",
                pointHoverBorderColor: "rgba(220,220,220,1)",
                pointHoverBorderWidth: 2,
                pointRadius: 1,
                pointHitRadius: 10,
                data: data,
            }
        ]
    };

    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            xAxes: [{
                display: false
            }]
        }
    });
}

function get_traffic_chart(){
    Sijax.request('get_traffic_chart', [Sijax.getFormValues('#network_form')]);
}

function get_faults(){
    Sijax.request('get_faults', [Sijax.getFormValues('#network_form')]);
}

function get_endpoint_track() {
    Sijax.request('get_endpoint_track', [Sijax.getFormValues('#network_form')]);
}