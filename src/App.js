import { Button, Menu, Select } from 'antd';
import React from 'react';
import 'antd/dist/antd.css'; // or 'antd/dist/antd.less'
import 'microphone-stream';
import io from 'socket.io-client';
import { VictoryChart, VictoryLine, VictoryLabel, VictoryTheme, VictoryScatter, VictoryLegend } from "victory";
import { blue, yellow, cyan, orange, green, magenta } from '@ant-design/colors';

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
      volumeData: [],
      tempoVolume: [{x: 0, y: 0}],
      pTempoVolumes: null,
      song: "Gymnopedie",
      printed: false
    };

    this.pieceChange = this.pieceChange.bind(this);
  }
  componentDidMount() {
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
          // take 1 seconds of samples
          if(this.state.lenSamples >= (winLength * audioContext.sampleRate) / 4096 ) {
            this.setState({lenSamples : 0 });
            this.state.socket.emit('tempo', this.state.song, true);
          }
        }
        this.state.socket.on('output local tempo', ({tempo, volume, p_volume, p_tempo}) => {
          this.setState({
            tempoData: [...this.state.tempoData, {x: this.state.tempoData.length * winLength, y: tempo}],
            // pTempoData: [...this.state.pTempoData, {x: this.state.pTempoData.length * winLength, y: p_tempo}],
            // pVolumeData: [...this.state.pVolumeData, {x: this.state.pVolumeData.length * winLength, y: p_volume}],
            volumeData: [...this.state.volumeData, {x: this.state.volumeData.length * winLength, y: volume}],
            tempoVolume: [{x: tempo, y: volume}],
            pTempoVolumes: {p_volume, p_tempo}
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
  getColors = (length) => {
    
    return [[magenta.primary, "Magenta"], [cyan.primary, "Cyan"], [yellow.primary, "Yellow"], [orange.primary, "Orange"], [green.primary, "Green"]];
  }
  render() {
    var scatters = [<VictoryScatter
      key="1"
      style={{
        data: { fill: blue.primary },
        parent: { border: "1px solid #ccc"}
      }}
      data= {this.state.tempoVolume}
      labels={({}) => "Me"}
    />];
    if(this.state.pTempoVolumes){
      console.log(this.state.pTempoVolumes)
      var colors = this.getColors();
      Object.keys(this.state.pTempoVolumes.p_tempo).forEach((performer, i) => {
        var volume = this.state.pTempoVolumes.p_volume[performer];
        var tempo = this.state.pTempoVolumes.p_tempo[performer];
        var tempoVolume = [{x : tempo, y : volume, label : performer}];  
        scatters.push(<VictoryScatter
          key={i}
          style={{
            data: { fill: colors[i][0] },
            parent: { border: "1px solid #ccc"}
          }}
          data={tempoVolume}
          labels={({ datum }) => datum.label}
        />);
      })
    }
    return (
      <>
        <div className="main-container">
          <div className="info-container">
          {/* <h3>Tempo(BPM)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
          >
            
            <VictoryLine
              // interpolation="natural"
              domain={{ y: [80, 160] }}
              style={{
                data: { stroke: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.tempoData}
            />
          </VictoryChart>
          <h3>Volume(db)</h3>
          <VictoryChart
            theme={VictoryTheme.material}
            domain={{ y: [70, 100] }}
          >
            <VictoryLine
              style={{
                data: { stroke: blue.primary },
                parent: { border: "1px solid #ccc"}
              }}
              data= {this.state.volumeData}
            />
          </VictoryChart>
           */}
          <VictoryChart
            theme={VictoryTheme.material}
            domain={{ x: [50, 200], y: [0, 200] }}
          >
            {scatters}
          </VictoryChart>
          </div>
          <div className="flex-row">
            <div className="center-console">
              <Button type="primary" onClick={() => this.enterLoading()}>
                Start
              </Button>
              <Button type="danger" onClick={() => this.stop()}>
                Stop
              </Button>
              <Select defaultValue="Gymnopedie" style={{ width: 300 }} onChange={this.pieceChange}>
                <Option value="Gymnopedie">Satie Gymnopedie</Option>
                <Option value="Nocturne">
                  Chopin Nocturne Op. 9 No. 2
                </Option>
                <Option value="Waltz 64 2">
                  Chopin Waltz Op. 64 No. 2
                </Option>
                <Option value="Waltz 69 1">Chopin Waltz Op. 69 No. 1</Option>
                <Option value="Waltz 69 2">
                  Chopin Waltz Op. 69 No. 2
                </Option>
                <Option value="Impromptu No 3">
                  Schubert Impromptu No. 3
                </Option>
                <Option value="Waltz A Minor">Chopin Waltz in Am</Option>
                <Option value="Fur Elise">
                  Beethoven Fur Elise
                </Option>
                <Option value="Traumerei">
                  Schumann Traumerei
                </Option>
                <Option value="Sonata">Mozart Sonata in C K.545</Option>
                <Option value="Minuet in F">
                  Bach Minuet in F
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