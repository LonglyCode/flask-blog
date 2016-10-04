var React = require("react");
var TodoForm = require('./TodoForm');
var TodoTable = require('./TodoTable');

var Todo = React.createClass({
    getInitialState: function(){
        return{
            todos:[]
        }
    },
    listTodo :function(){
        $.ajax({
            type:'get',
            url:'/list'
        }).done(function(resp){
            if(resp.status=='success'){
                this.setState({todos:resp.todos})
            }
        }.bind(this))
    },
    addTodo :function(){
        $.ajax({
            type:'post',
            url:'add',
            data:{content:content}
        }).done(function(resp){
            if(resp.status=='success'){
                this.listTodo();
           }
        }.bind(this))
    },
    componentDidMount:function(){
        this.listTodo();
    },
    render : function(){
        return(
                <div>
                <TodoForm addTodo = {this.addTodo} />
                <TodoTable todos = {this.state.todos} />
                </div>
        )
    }
});

module.exports = Todo;
