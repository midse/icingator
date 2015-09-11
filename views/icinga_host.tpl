// <ICINGATOR_BEGIN>
// modified on {{dateandtime}}
object Host "{{sysname}}" {
    import "generic-host"

    display_name    = "{{sysname}}"
    address         = "{{host}}"
    groups          += [ "{{device_type}}", "{{location}}" ]

    vars.os         =  "{{device_type}}"

    % for interface in interfaces:
    % interface_name, interface_id = interface.split('#')
    vars.interfaces["{{interface_name}}"] = "{{interface_id}}"
    %end
}
// </ICINGATOR_END>
