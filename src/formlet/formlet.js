
Formlet.Widget = Nevow.Athena.Widget.subclass('Formlet.Widget');
Formlet.Form = Formlet.Widget.subclass("Formlet.Form");

function executeFunctionByName(functionName, context /*, args */) {
  var args = Array.prototype.slice.call(arguments).splice(2);
  var namespaces = functionName.split(".");
  var func = namespaces.pop();
  for(var i = 0; i < namespaces.length; i++) {
    context = context[namespaces[i]];
  }
  return context[func].apply(this, args);
}

Formlet.Form.methods(

    function submit(self, node, ev) {
        ev.preventDefault();
        var fields = {};
        _.map(node, function (elem) {
            fields[elem.name] = elem.value;
        });
        return self.callRemote("process", fields);
    }
);
