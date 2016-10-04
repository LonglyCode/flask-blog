var React = require("react");

var TodoForm = React.createClass({
    render : function(){
        return(
                <form>
                     <input ref="content" className="form-control" id="content" name="add"/>
                <span className="input-group-btn">
                     <button className="btn btn-default" type="submit">add</button>
                </span>
                </form>
        )
    }
});

module.exports = TodoForm;
