import React from 'react';
import Board from '../components/Board'
import Grid from '@mui/material/Grid'
import Box from '@mui/material/Box'
import Chess from "chess.js";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

class IndexPage extends React.Component{
    constructor(props){
        super(props);

        this.board = React.createRef()

        this.state ={
            moves: [],
            game: null,
            sortedLines: [],
            lines: {},
            engine: null,
            engineReady:false,
            depth: 0,
            eval: 0,
            nps:0,
            mate: null,
        }
    }

    componentDidMount(){
        const engine = new Worker("/stockfish.js");
        var i = 0
        engine.onmessage = (msg) => {
            //console.log(msg.data)
            if(msg.data == "uciok"){
                this.setState({engineReady:true})
            } else if(msg.data.startsWith("info")){
                const keys = ["depth", "cp", "mate", "nps", "pv", "multipv"]
                let mapped = {
                }
                let split = msg.data.split(" ")
                split.shift()

                for(let i=0;i<split.length;i++){
                    let key = split[i]
                    if(keys.indexOf(key) !== -1){
                        if(key == "pv"){
                            mapped[key] = split.slice(i+1, split.length-1)
                        } 
                        else{
                            mapped[key] = split[i+1]
                        }
                        
                    } 
                }
                if(mapped.hasOwnProperty("cp")){
                    if(Number(mapped["depth"]) >= Number(this.state.eval.depth)){
                        if(Number(mapped["depth"]) == Number(this.state.eval.depth)){
                            if(mapped["cp"] > this.state.eval.cp){
                                mapped["eval"] = {
                                    cp: mapped["cp"],
                                    depth: mapped["depth"]
                                }
                            }
                        } else{
                            mapped["eval"] = {
                                cp: mapped["cp"],
                                depth: mapped["depth"]
                            }
                        }
                        

                    }
                }
                if(mapped.hasOwnProperty("pv") && mapped.pv.length > 0){
                    let game = new Chess(this.board.current.state.game.fen())
                    let move = game.move({ from: mapped["pv"][0].slice(0,2), to: mapped["pv"][0].slice(2,4) })
                    if(!move){
                        return;
                    }
                    let move_str = move.san
                    let line = {
                        "move": move_str,
                        "gameCount": 45000, 
                        "results": "50% | 10% | 40%", 
                        "eval": mapped["cp"] * (this.state.moves.length % 2 != 0 ? -1:1),
                        "depth": mapped["depth"]
                    }
                    
                    this.state.lines[move_str] = line
                    mapped["lines"] = this.state.lines;
                    mapped["sortedLines"] = Object.values(this.state.lines).sort((a,b) => (b.eval - a.eval) * (this.state.moves.length % 2 != 0 ? -1:1))

                    let best_line = mapped["sortedLines"][0]
                    if(best_line.hasOwnProperty("depth")){
                        mapped["depth"] = best_line["depth"]
                    }
                    if(best_line.hasOwnProperty("eval") && best_line["eval"]){
                        mapped["eval"] = best_line["eval"]
                    }
                }


                this.setState(mapped)
            }
        }
        engine.postMessage("uci");
        engine.postMessage("setoption name MultiPV value 4");
        engine.postMessage("setoption name Threads value " + window.navigator.hardwareConcurrency -2);
		
		engine.postMessage("setoption name wdldrawratereference value 0.58");
		engine.postMessage("setoption name wdlcalibrationelo value 2700");
		engine.postMessage("setoption name contempt value 400");
		engine.postMessage("setoption name contemptmode value play");
		engine.postMessage("setoption name wdlcontemptattenuation value 0.5");

        engine.postMessage("ucinewgame");
        this.setState({engine:engine});
    }

    onMove(move, game){
        this.setState({moves: game.history(), lines:[], sortedLines: [], eval:0, depth:0})
        
        this.state.engine.postMessage("stop");
        this.state.engine.postMessage("position fen " + game.fen());
        this.state.engine.postMessage("go")
    }

    render(){
        return (
        <Grid container spacing={0}>
            <Grid xs={6}>
                <button onClick={() => {this.state.engine.postMessage("stop");}}>Stop engine</button>
                <Board ref={this.board} onMove={this.onMove.bind(this)} initialFen={'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'}/>
            </Grid>
            <Grid xs={6}>
                <Box style={{background:"#3e419c", borderRadius:"10px"}} height={"99%"} mx={2}>
                    <Grid container spacing={0} p={2} style={{height:"calc(100% - 300px)"}}> 
                        <Grid xs={9} style={{background: "#2a2c63", borderRadius:"10px", height:"100%"}} p={2}>
                            <p style={{color:"#fff"}}>{this.state.moves.join(" ")}</p>
                        </Grid>
                        <Grid xs={3}>
                            <h2 style={{textAlign:"right", color:"#fff", margin:0}}>Stockfish 16</h2>
                            <h2 style={{textAlign:"right", color:"#fff", margin:0}}>depth: {this.state.depth}</h2>
                            <h2 style={{textAlign:"right", color:"#fff", margin:0}}>{Math.round(Number(this.state.nps)/1000)} KNodes/s</h2>
                            <h2 style={{textAlign:"right", color:"#fff", margin:0}}>{this.state.eval/100}</h2>
                        </Grid>
                    </Grid>
                    <Grid container spacing={0} p={2} style={{height:"300px"}}>
                        <TableContainer style={{background: "#2a2c63", height:"100%", width:"100%", borderRadius:"10px"}} component={Paper}>
                            <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
                                <TableHead>
                                <TableRow>
                                    <TableCell style={{color:"#fff"}}>Move</TableCell>
                                    <TableCell align="right" style={{color:"#fff"}}>Games</TableCell>
                                    <TableCell align="right" style={{color:"#fff"}}>Result</TableCell>
                                    <TableCell align="right" style={{color:"#fff"}}>Evaluation</TableCell>
                                </TableRow>
                                </TableHead>
                                <TableBody>
                                    {this.state.sortedLines.map((itm) => {
                                        return (
                                        <TableRow onClick={() => {this.board.current.makeAMove(itm.move)}} key={itm.move} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                                            <TableCell style={{color:"#fff"}}>{itm.move}</TableCell>
                                            <TableCell style={{color:"#fff"}} align="right">{itm.gameCount}</TableCell>
                                            <TableCell style={{color:"#fff"}} align="right">{itm.results}</TableCell>
                                            <TableCell style={{color:"#fff"}} align="right">{itm.eval/100}</TableCell>
                                        </TableRow>
                                        )
                                    })}
                                    
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Grid>
                </Box>
            </Grid>
        </Grid>
        );
    }
}

export default IndexPage