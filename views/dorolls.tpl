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

    </div><!-- /.container -->

 % include("footer.tpl")
