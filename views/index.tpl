% include('header.tpl')

    <div class="pure-g">
      <div class="pure-u-1 pure-u-md-1-2">
          <form class="box pure-form" action="" id="do_device">
                  <input name="host" type="text" placeholder="Host">
                    <select name="device_type">
                      % for device_type in device_types:
                        <option value="{{device_type}}">{{device_type}}</option>
                      %end
                    </select>
                  <button type="submit" class="pure-button pure-button-primary">Fetch</button>
          </form>
      </div>
      <div class="pure-u-1 pure-u-md-1-2">
        <form class="box pure-form" action="" id="do_conf">
                <select name="conf_file">
                  % for conf_file in conf_files:
                    <option value="{{conf_file}}">{{conf_file}}</option>
                  %end
                </select>
                <button type="submit" class="pure-button pure-button-primary">Modify</button>
        </form>
      </div>
    </div>

    <div id="device_output">
    </div>

    <div id="icinga_output">
    </div>

    <script>
        $(function(){
            $("#do_device").submit(function(e){
                e.preventDefault();
                var formData = $("#do_device").serializeArray();

                $.ajax({type: "POST",
                        url: "/device",
                        data:formData,
                        beforeSend: function(){
                          $("#device_output").html('<br><br><img src="ajax-loader.gif" style="margin-left:50px;"/>');
                          $("#icinga_output").html('');
                        },
                        success: function(data){
                          $("#device_output").html(data);
                        }});
                });
        });

        $(function(){
            $("#do_conf").submit(function(e){
                e.preventDefault();
                var formData = $("#do_conf").serializeArray();

                $.ajax({type: "POST",
                        url: "/conf",
                        data:formData,
                        beforeSend: function(){
                          $("#device_output").html('<br><br><img src="ajax-loader.gif" style="margin-left:50px;"/>');
                          $("#icinga_output").html('');
                        },
                        success: function(data){
                          $("#device_output").html(data);
                        }});
                });

        });
    </script>

% include('footer.tpl')
