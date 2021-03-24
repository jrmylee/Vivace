import { Button, Menu, Select } from 'antd';
import React from 'react';
import 'antd/dist/antd.css'; // or 'antd/dist/antd.less'
import 'microphone-stream';
import io from 'socket.io-client';
import { VictoryChart, VictoryLine, VictoryTheme, VictoryScatter, VictoryLegend } from "victory";
import { blue, magenta, cyan } from '@ant-design/colors';

const { Option } = Select;

class App extends React.Component {
  
  constructor(props) {
    super(props);
    var socket = io("http://localhost:5000/test");
    this.state = {
      started : false,
      microphone : null,
      socket: socket,
      lenSamples : 0,
      globalTempo: "none",
      globalVolume: "none",
      tempoData: [],
      pTempoData: [],
      volumeData: [],
      pVolumeData: [],
      tempoVolume: [{x: 0, y: 0}],
      song: "widmung"
    };

    this.pieceChange = this.pieceChange.bind(this);
  }
  enterLoading = () => {
    var ob = this;
    this.state.socket.connect();
    navigator.mediaDevices
      .getUserMedia({ audio: true }).then((stream) => {
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var source = audioContext.createMediaStreamSource(stream);
        var node = audioContext.createScriptProcessor(4096, 1, 1);
        var winLength = 1;
        this.state.socket.emit('sample_rate', audioContext.sampleRate);
        
        node.onaudioprocess = (audioProcessingEvent) => {
            // The input buffer is the song we loaded earlier
          let inputBuffer = audioProcessingEvent.inputBuffer;
          var left = inputBuffer.getChannelData(0);
          var obj = {};
          left.forEach((elem, i) => {
            obj[i] = elem;
          })
          this.state.socket.emit("send_audio", obj);
          this.setState({lenSamples : this.state.lenSamples + 1})
          // take 3 seconds of samples
          if(this.state.lenSamples >= 3 * (winLength * audioContext.sampleRate) / 4096 ) {
            this.setState({lenSamples : 0 });
            this.state.socket.emit('tempo', this.state.song, true);
          }
        }
        this.state.socket.on('output local tempo', ({tempo, volume, p_volume, p_tempo}) => {
          this.setState({
            // tempoData: [...this.state.tempoData, {x: this.state.tempoData.length * winLength, y: tempo}],
            pTempoData: [...this.state.pTempoData, {x: this.state.pTempoData.length * winLength, y: p_tempo}],
            pVolumeData: [...this.state.pVolumeData, {x: this.state.pVolumeData.length * winLength, y: p_volume}],
            // volumeData: [...this.state.volumeData, {x: this.state.volumeData.length * winLength, y: volume}],
            // tempoVolume: [{x: tempo, y: volume}],
            pTempoVolume: [{x: p_tempo, y: p_volume}]
          })
        })
        this.state.socket.on('output global tempo', ({tempo, volume}) => {
          this.setState({
            globalTempo : tempo + " BPM",
            globalVolume : volume + "db"
          })
        })
        // Connect the microphone to the script processor
        source.connect(node);
        node.connect(audioContext.destination);

        this.setState({
          source: source,
          node: node
        })
      });
  };
  stop = () => {
    if(this.state.source){
      this.state.socket.emit("tempo", this.state.song, false);
      console.log(this.state.signal);
      this.state.node.disconnect();
      this.state.source.disconnect();
      this.setState({
        source: null,
        node: null,
      });
    }
  };
  pieceChange = (song) => {
    console.log(song);
    this.setState({
      song: song
    })
  };
  windowChange = () => {

  }
  render() {
    return (
      <>
        <div className="main-container">
          <div className="info-container">
          <VictoryLegend x={125} y={10}
            title="Performer Legend"
            centerTitle
            orientation="horizontal"
            gutter={20}
            colorScale={["blue", "cyan" ]}
            data={[
              { name: "User" }, { name: "Performer" }
            ]}
          />
          <h3>Tempo(BPM)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
          >
            
            {/* <VictoryLine
              // interpolation="natural"
              style={{
                data: { stroke: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.tempoData}
            /> */}
            <VictoryLine
              // interpolation="natural"
              style={{
                data: { stroke: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pTempoData}
            />
          </VictoryChart>
          <h3>Volume(db)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
          >
            {/* <VictoryLine
              style={{
                data: { stroke: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.volumeData}
            /> */}
            <VictoryLine
              style={{
                data: { stroke: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pVolumeData}
            />
          </VictoryChart>
          <h3>Tempo vs Volume</h3>
          <VictoryChart
            theme={VictoryTheme.material}
            domain={{ x: [70, 200], y: [70, 150] }}
          >
            {/* <VictoryScatter
              style={{
                data: { fill: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.tempoVolume}
            /> */}
            <VictoryScatter
              style={{
                data: { fill: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pTempoVolume}
            />
          </VictoryChart>
          </div>
          <div className="flex-row">
            <div>
              <h3>Global Tempo: {this.state.globalTempo}</h3>
              <h3>Global Volume: {this.state.globalVolume}</h3>
            </div>
            <div className="center-console">
              <Button type="primary" onClick={() => this.enterLoading()}>
                Start
              </Button>
              <Button type="danger" onClick={() => this.stop()}>
                Stop
              </Button>
              <Select defaultValue="widmung" style={{ width: 300 }} onChange={this.pieceChange}>
                <Option value="widmung">Widmung by Schumann/Liszt</Option>
                <Option value="etude">
                  Scriabin Etude Op. 42 no 5
                </Option>
                <Option value="desabends">
                  Schumann Fantasiestucke Op. 12 no 1
                </Option>
              </Select>
            </div>
          </div>
        </div>
      </>
    );
  }
}

export default App;