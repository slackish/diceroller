 % include("header.tpl", title="Main")
    <div class="container">

      <div class="starter-template">
        <h1>Roll some dice:</h1>
        <p>So you want to roll some dice, eh?</p>
        <p>
        You can specify which dice to roll by saying something like
        "1d20", which will roll one 20 sided die. 3d6 will roll three 6
        sided dice.  More complex rolls involving different dice can be
        done by separating dice by commas. </p>

        <samp>1d20,1d6</samp>
        Will result in
        <samp>1d20,2d6: 18 + 4 + 3 = 25</samp>

        <p>Others can view rolls at:<samp><div id="page"></div><samp>

        <form name="rollform" action="" onsubmit="return validateRoll()">
          <input type="text" id="inputroll" name="chat">
          <input type="submit" value="submit">
        </form>
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

      // load some page stuff
      vieweruri = loc.protocol + loc.host + loc.pathname;
      vieweruri = vieweruri.replace("roll", "view");
      $("#page").text(vieweruri);

      // well crap, no relative paths to websockets
      var loc = window.location, ws_uri;
      if (loc.protocol === "https:") {
          ws_uri = "wss:";
      } else {
          ws_uri = "ws:";
      }
      ws_uri += "//" + loc.host + loc.pathname + "/ws";

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
          current_text = $("#rolls").html(new_text)
      }
      </script>

    </div><!-- /.container -->

 % include("footer.tpl")
