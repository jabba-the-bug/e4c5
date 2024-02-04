import React from 'react';
import Chess from "chess.js";
import { Chessboard } from "react-chessboard";

class Board extends React.Component{
    constructor(props){
        super(props);

        this.state ={
            game: new Chess(props.initialFen),
        }
    }
    makeAMove(move) {
        
        const result = this.state.game.move(move);
        if(result){
            console.log(move)
            this.setState({game:this.state.game});
            this.props.onMove(move, this.state.game);
        }
        return result; // null if the move was illegal, the move object if the move was legal
    }
    onDrop(sourceSquare, targetSquare) {
        const move = this.makeAMove({
            from: sourceSquare,
            to: targetSquare,
            promotion: "q", // always promote to a queen for example simplicity
        });

        // illegal move
        if (move === null) return false;
        return true;
    }

    render(){
        return <div style={{maxHeight:"99%", maxWidth:"100%"}}><Chessboard position={this.state.game.fen()} onPieceDrop={this.onDrop.bind(this)} /></div>;
    }
}

export default Board