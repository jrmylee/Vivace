import { Button, Menu, Select } from 'antd';
import React from 'react';
import 'antd/dist/antd.css'; // or 'antd/dist/antd.less'
import 'microphone-stream';
import io from 'socket.io-client';
import { VictoryChart, VictoryLine, VictoryTheme, VictoryScatter } from "victory";
import { blue, magenta, cyan } from '@ant-design/colors';

const { Option } = Select;

class App extends React.Component {
  
  constructor(props) {
    super(props);
    var socket = io("https://www.tonetwelve.com/test");
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
      tempoVolume: [{x: 0, y: 0}]
    };
  }
  menu = (
    <Menu>
      <Menu.Item>
        <a target="_blank" rel="noopener noreferrer" href="http://www.alipay.com/">
          1 sec
        </a>
      </Menu.Item>
      <Menu.Item>
        <a target="_blank" rel="noopener noreferrer" href="http://www.taobao.com/">
          2 sec
        </a>
      </Menu.Item>
      <Menu.Item>
        <a target="_blank" rel="noopener noreferrer" href="http://www.tmall.com/">
          3 sec
        </a>
      </Menu.Item>
    </Menu>
  );
  pieces = (
    <Menu>
      <Menu.Item>
        <a target="_blank" rel="noopener noreferrer" href="http://www.alipay.com/">
          Schumann/Liszt Widmung(Trifonov)
        </a>
      </Menu.Item>
    </Menu>
  )
  enterLoading = () => {
    var ob = this;
    this.state.socket.connect();
    navigator.mediaDevices
      .getUserMedia({ audio: true }).then((stream) => {
        var audioContext = new (window.AudioContext || window.webkitAudioContext)();
        var source = audioContext.createMediaStreamSource(stream);
        var node = audioContext.createScriptProcessor(4096, 1, 1);
        this.state.socket.emit('sample_rate', audioContext.sampleRate);
        
        node.onaudioprocess = (audioProcessingEvent) => {
            // The input buffer is the song we loaded earlier
          let inputBuffer = audioProcessingEvent.inputBuffer;
          var left = inputBuffer.getChannelData(0);
          var obj = {};
          left.forEach((elem, i) => {
            obj[i] = elem;
          })
          this.state.socket.emit("message", obj);
          this.setState({lenSamples : this.state.lenSamples + 1})
          // take 3 seconds of samples
          if(this.state.lenSamples >= (3 * audioContext.sampleRate) / 4096 ) {
            this.setState({lenSamples : 0 });
            this.state.socket.emit('tempo', true);
          }
        }
        this.state.socket.on('output local tempo', ({tempo, volume}) => {
          this.setState({
            tempoData: [...this.state.tempoData, {x: this.state.tempoData.length * 3, y: tempo}],
            // pTempoData: [...this.state.pTempoData, {x: this.state.tempoData.length * 3, y: p_tempo}],
            // pVolumeData: [...this.state.pVolumeData, {x: this.state.volumeData.length * 3, y: p_volume}],
            volumeData: [...this.state.volumeData, {x: this.state.volumeData.length * 3, y: volume}],
            tempoVolume: [{x: tempo, y: volume}],
            // pTempoVolume: [{x: p_tempo, y: p_volume}]
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
      this.state.socket.emit("tempo", false);
      console.log(this.state.signal);
      this.state.node.disconnect();
      this.state.source.disconnect();
      this.setState({
        source: null,
        node: null,
      });
    }
  };
  pieceChange = () => {

  };
  windowChange = () => {

  }
  render() {
    return (
      <>
        <div className="main-container">
          <div className="info-container">
          <h3>Tempo(BPM)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
          >
            <VictoryLine
              interpolation="natural"
              style={{
                data: { stroke: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.tempoData}
            />
            {/* <VictoryLine
              interpolation="natural"
              style={{
                data: { stroke: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pTempoData}
            /> */}
          </VictoryChart>
          <h3>Volume(db)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
          >
            <VictoryLine
              style={{
                data: { stroke: magenta.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.volumeData}
            />
            {/* <VictoryLine
              style={{
                data: { stroke: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pVolumeData}
            /> */}
          </VictoryChart>
          <h3>Tempo vs Volume</h3>
          <VictoryChart
            theme={VictoryTheme.material}
            domain={{ x: [70, 200], y: [70, 150] }}
          >
            <VictoryScatter
              style={{
                data: { fill: cyan.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.tempoVolume}
            />
            {/* <VictoryScatter
              style={{
                data: { fill: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.pTempoVolume}
            /> */}
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
              <Select defaultValue="widmung" style={{ width: 120 }} onChange={() => this.pieceChange()}>
                <Option value="widmung">Widmung</Option>
              </Select>
              <Select defaultValue="3" style={{ width: 120 }} onChange={() => this.windowChange()}>
                <Option value="3">3 Secs</Option>
                <Option value="3">6 Secs</Option>
                <Option value="3">9 Secs</Option>
              </Select>
            </div>
          </div>
        </div>
      </>
    );
  }
}

export default App;