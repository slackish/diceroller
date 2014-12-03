 % include("header.tpl", title="Main")
    <div class="container">

      <div class="starter-template">
        <h1>See some dice:</h1>
        <p>Others can view rolls at:<samp><div id="page"></div><samp>
        <p>Roll log: </p>
        <ul>
        <div id="rolls"></div>
        </ul>

      </div>

      <script>

      function validateRoll() {
          ws.send("1,"+document.forms["rollform"]["inputroll"].value);
          return false;
      }


      // well crap, no relative paths to websockets
      var loc = window.location, ws_uri;
      if (loc.protocol === "https:") {
          ws_uri = "wss:";
          vieweruri = "https:";
      } else {
          ws_uri = "ws:";
          vieweruri = "http:";
      }
      ws_uri += "//" + loc.host + loc.pathname + "/ws";

      window.onload = function() {
          // load some page stuff
          vieweruri += "//" + loc.host + loc.pathname;
          vieweruri = vieweruri.replace("roll", "view");
          $("#page").text(vieweruri);
      }

      var ws = new WebSocket(ws_uri);
    
      ws.onopen = function() {
          ws.send("0,chkin")
      }
      ws.onmessage = function(evt) {
          op = evt.data.split(",", 1);
          op = String(op);
          msg = evt.data.slice(op.length + 1);
          console.log(op.length + 1);
          op = parseInt(op);
          handle_ws(op, msg);
      };

      function handle_ws(op, msg) {
            console.log("received " + op + ", with msg'" + msg + "'");
            console.log(typeof(op));
            switch (op) {
                case 0:
                    console.log("You shouldn't see op 0 here");
                case 1:
                    append_roll(msg)
                    break;
                default:
                    console.log("whoops, I can't handle that");
            }
      }  

      function append_roll(msg) {
          new_text = "<li>"+msg+"</li>"+ $("#rolls").html();
          $("#rolls").html(new_text);
      }
      </script>

    </div><!-- /.container -->

 % include("footer.tpl")
