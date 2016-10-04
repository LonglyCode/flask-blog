var React = require("react");

var TodoItem = React.createClass({
    handleUpdate:function(id,status){
        this.props.updateTodo(id,status);
    },
    render : function(){
        var t = this.props.todo;
        var updateBtn;
        if(t.status==0){
            updateBtn=<button onClick={this.handleUpdate.bind(this,t.id,1)} className="btn">DONE</button>;
        }else{
            updateBtn=<button onClick={this.handleUpdate.bind(this,t.id,0)} className="btn">UnDONE</button>;
        }
        return(
                <tr>
                <td>{ t.content }</td>
                <td>{ t.status==0 ? '未完成':'已完成' }</td>
                <td>{ t.time }</td>
                <td>
                {updateBtn}
                <button className="btn">Delete</button>
                </td>
                </tr>
                )
    }
});

module.exports = TodoItem;
