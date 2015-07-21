<!DOCTYPE html>
<html lang="en">
<head>
<title>{{title}}</title>
<style type="text/css" media="screen">
  *, html, body {
    margin: 0;
    padding: 0;
  }

  #editor {
      width: 500px;
      height: 100vh;
      /*position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;*/
  }
</style>
</head>
<body>

<div id="editor">from chef import *


def main():
    """ This is a comment and you code goes in the
    line bellow, where it says pass """
    pass

if __name__ == '__main__':
    main()
</div>

<script src="/resources/js/ace-builds/src-noconflict/ace.js" type="text/javascript" charset="utf-8"></script>
<script>
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode("ace/mode/python");
</script>
</body>
</html>
