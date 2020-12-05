var populate_dropdown = function (id, items) {
    console.log(id);
    var dropdown = document.getElementById(id);
    items.forEach(item => {
        var elem = document.createElement("option")
        elem.setAttribute("value", item.value);
        elem.innerHTML = item.ui_name;
        dropdown.appendChild(elem);
    })
}


window.onload = function() {
    function onFreq(re, im) {
        //Frequency stuff.  Process it here
        console.log(re)
        console.log(im)
        istft(re, im)
    }
    
    function onTime(v) {
        //Got data, emit it here
        console.log("o");
        console.log("out frame:", v)
    }
    
    var stft = shortTimeFT(1, 1024, onFreq, { hop_size : 441})
    var istft = shortTimeFT(-1, 1024, onTime)
    
    //Feed stuff into signal
    stft(new Float32Array([1, 0, 0, 0 ]));

    var pieces = [
        {value: "mazurka1", ui_name: "Marzuka Op 6 no 2"}
    ];
    
    populate_dropdown('piece-dropdown', pieces);
}

console.clear();

// UPDATE: there is a problem in chrome with starting audio context
//  before a user gesture. This fixes it.
var started = null;
window.addEventListener('click', () => {
  if (started) return;
  started = true;
  initialize();
})

function initialize() {
    var aCtx;
var analyser;
var microphone;
if (navigator.getUserMedia) {
    navigator.mediaDevices
    .getUserMedia({ audio: true }).then(function(stream) {
        console.log("top");
        aCtx = new AudioContext();
        analyser = aCtx.createAnalyser();
        analyser.fftSize = 1024;

        N = analyser.frequencyBinCount;

        microphone = aCtx.createMediaStreamSource(stream);
        microphone.connect(analyser);
        // analyser.connect(aCtx.destination);
        process(N);
        console.log(aCtx.sampleRate)
    });
};

// Params: 
//  X is the STFT frame of audio input x
//  N is the number of FFT bins
// Returns:
//  The HFC detection function at the given STFT frame
function hfc(X, N){
    let detectionFn = 0;
    for(var k = 0; k < N; k++){
        detectionFn += k * Math.abs(X[k])
    }
    return detectionFn;
}

function process(N){
    console.log(N);
    setInterval(function(){
        FFTData = new Float32Array(analyser.frequencyBinCount);
        analyser.getFloatFrequencyData(FFTData);
        console.log(FFTData);
    },10);
}
    
}
