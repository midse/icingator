
             <h2>{{sysname}}</h2>

             We got <strong>{{nb_interfaces}} interfaces</strong> from {{host}}<br><br>

             We found that some interfaces are already monitored : <br><br>

            <form class="pure-form pure-form-stacked" action="" id="do_icinga">
                <div class="pure-g">
                  <div class="pure-u-1 pure-u-md-1-4">
                    <input type="checkbox" id="selectall" hidden/> <label for="selectall" class="pure-button button-secondary">Select or deselect all interfaces</label>
                  </div>
                  <div class="pure-u-1 pure-u-md-1-4"></div>
                  <div class="pure-u-1 pure-u-md-1-4"></div>
                  <div class="pure-u-1 pure-u-md-1-4"></div>

                  <div class="pure-u-4"></div>

                  <div class="pure-u-1 pure-u-md-1-4">
                    <h4>Interface name</h4>
                  </div>

                  <div class="pure-u-1 pure-u-md-1-4">
                    <h4>Type</h4>
                  </div>

                  <div class="pure-u-1 pure-u-md-1-4">
                    <h4>Status</h4>
                  </div>

                  <div class="pure-u-1 pure-u-md-1-4">
                    <h4>Alias</h4>
                  </div>

                  %for index, my_tuple in enumerate(interfaces):
                      %    interface_status = '<span class="button-success pure-button">UP</span>' if my_tuple[1][2] == 1 else '<span class="button-error pure-button">DOWN</span>'
                      %    interface_alias = my_tuple[1][1]
                      %    interface_name = my_tuple[1][0]
                      %    interface_type = my_tuple[1][3]
                      %    interface_id = str(my_tuple[0])
                      %    checked = 'checked="checked"' if interface_id in oids else ''

                      <div class="pure-u-1 pure-u-md-1-4">
                        <label for="{{interface_id}}"><input type="checkbox" {{checked}} class="checkbox" value="{{interface_name}}#{{interface_id}}" id="{{interface_id}}" name="interfaces"> {{interface_name}}</label>
                      </div>
                      <div class="pure-u-1 pure-u-md-1-4">
                        <label for="{{interface_id}}">{{interface_type}}</label>
                      </div>
                      <div class="pure-u-1 pure-u-md-1-4">
                        <label for="{{interface_id}}">{{!interface_status}}</label>
                      </div>
                      <div class="pure-u-1 pure-u-md-1-4">
                        <label for="{{interface_id}}">{{interface_alias}}</label>
                      </div>
                    %end
                </div>

                <br><br>
                <input type="hidden" name="host" value="{{host}}">
                <input type="hidden" name="device_type" value="{{device_type}}">
                <button type="submit" class="pure-button pure-button-primary">Generate configuration file</button>
            </form>

            <script>
              $(function(){
                  $("#do_icinga").submit(function(e){
                      e.preventDefault();

                      var formData = $("#do_icinga").serializeArray();

                      $.ajax({type: "POST",
                              url: "/icinga",
                              data:formData,
                              beforeSend: function(){
                                $("#icinga_output").html('<br><br><img src="ajax-loader.gif" style="margin-left:50px;"/>');
                              },
                              success: function(data){
                                $("#icinga_output").html(data);
                              }});
                      });
                      });

              $(function() {
                  $('#selectall').click(function(event) {  //on click
                      if(this.checked) { // check select status
                          $('.checkbox').each(function() { //loop through each checkbox
                              this.checked = true;  //select all checkboxes with class "checkbox1"
                          });
                      }else{
                          $('.checkbox').each(function() { //loop through each checkbox
                              this.checked = false; //deselect all checkboxes with class "checkbox1"
                          });
                      }
                  });
              });


            </script>
