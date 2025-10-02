// Select elements with updated class names
let track_name = document.querySelector(".player-songtitle");
let playpause_btn = document.querySelector(".player-playpause-track");
let next_btn = document.querySelector(".player-next-track");
let prev_btn = document.querySelector(".player-prev-track");

let seek_slider = document.querySelector(".player-seek-slider");
let curr_time = document.querySelector(".player-current-time");
let total_duration = document.querySelector(".player-total-duration");

let track_index = 0;
let isPlaying = false;
let updateTimer;

let curr_track = document.getElementById("player-music");

// Define your tracks
let track_list = [
    { name:"Brain Fluid Explosion Girl - Will Stetson (old ver.)", path:"https://file.garden/aBi0tvXzESnPXzr_/songs/SpotiDown.App%20-%20Brain%20Fluid%20Explosion%20Girl%20-%20Will%20Stetson.mp3" },
    { name:"Miss Missing You - Fallout Boy", path:"https://file.garden/aBi0tvXzESnPXzr_/songs/%5BSPOTDOWNLOADER.COM%5D%20Miss%20Missing%20You.mp3" },
    { name:"Ruler of Everything - Tally Hall", path:"https://file.garden/aBi0tvXzESnPXzr_/songs/%5BSPOTDOWNLOADER.COM%5D%20Ruler%20of%20Everything.mp3" },
    { name:"Television Romance - Pale Waves", path:"https://file.garden/aBi0tvXzESnPXzr_/songs/%5BSPOTDOWNLOADER.COM%5D%20Television%20Romance.mp3" },
    { name:"ATTACKING VERTICAL - femtanyl", path:"https://file.garden/aBi0tvXzESnPXzr_/songs/%5BSPOTDOWNLOADER.COM%5D%20ATTACKING%20VERTICAL.mp3" }
];

// Load a track by index
function loadTrack(index) {
    clearInterval(updateTimer);
    resetValues();
    curr_track.src = track_list[index].path;
    curr_track.load();
    track_name.textContent = track_list[index].name;
    updateTimer = setInterval(seekUpdate, 1000);
    curr_track.addEventListener("ended", nextTrack);
}

// Reset slider and time
function resetValues() {
    curr_time.textContent = "0:00";
    total_duration.textContent = "0:00";
    seek_slider.value = 0;
}

// Play/pause toggle
function playpauseTrack() {
    if (!isPlaying) playTrack();
    else pauseTrack();
}

// Play track
function playTrack() {
    curr_track.play();
    isPlaying = true;
    playpause_btn.querySelector("img").src = "https://files.catbox.moe/njer0s.png"; // pause icon
}

// Pause track
function pauseTrack() {
    curr_track.pause();
    isPlaying = false;
    playpause_btn.querySelector("img").src = "https://files.catbox.moe/w93riq.png"; // play icon
}

// Next track
function nextTrack() {
    track_index = (track_index + 1) % track_list.length;
    loadTrack(track_index);
    playTrack();
}

// Previous track
function prevTrack() {
    track_index = (track_index - 1 + track_list.length) % track_list.length;
    loadTrack(track_index);
    playTrack();
}

// Seek to a point in the track
function seekTo() {
    let seekto = curr_track.duration * (seek_slider.value / 100);
    curr_track.currentTime = seekto;
}

// Update slider and time display
function seekUpdate() {
    if (!isNaN(curr_track.duration)) {
        let seekPosition = curr_track.currentTime * (100 / curr_track.duration);
        seek_slider.value = seekPosition;

        let currentMinutes = Math.floor(curr_track.currentTime / 60);
        let currentSeconds = Math.floor(curr_track.currentTime % 60);
        let durationMinutes = Math.floor(curr_track.duration / 60);
        let durationSeconds = Math.floor(curr_track.duration % 60);

        if (currentSeconds < 10) { currentSeconds = "0" + currentSeconds; }
        if (durationSeconds < 10) { durationSeconds = "0" + durationSeconds; }

        curr_time.textContent = currentMinutes + ":" + currentSeconds;
        total_duration.textContent = durationMinutes + ":" + durationSeconds;
    }
}

// Load the first track on page load
loadTrack(track_index);


//////////// all of that above was forked

// notepad

function saveNotepad() {
  const text = document.getElementById('notepad-text').value;
  localStorage.setItem('notepad', text);
}

window.onload = () => {
  const saved = localStorage.getItem('notepad');
  if(saved) document.getElementById('notepad-text').value = saved;
};

function closeWindow(id) {
  document.getElementById(id).style.display = 'none';
}
function downloadNotepad() {
    const text = document.getElementById('notepad-text').value;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'note.txt'; // default file name
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url); // cleanup
}


////////// pixel art

const canvas = document.getElementById('pixelart-canvas');
const ctx = canvas.getContext('2d');
const colorPicker = document.getElementById('color-picker');

let drawing = false;

// draw pixels
canvas.addEventListener('mousedown', () => drawing = true);
canvas.addEventListener('mouseup', () => drawing = false);
canvas.addEventListener('mouseleave', () => drawing = false);

canvas.addEventListener('mousemove', function(e) {
    if (!drawing) return;
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - rect.left) / 10) * 10;
    const y = Math.floor((e.clientY - rect.top) / 10) * 10;
    ctx.fillStyle = colorPicker.value;
    ctx.fillRect(x, y, 10, 10);
});

// clear canvas
function clearPixelArt() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// download as a png for transparency
function downloadPixelArt() {
    const link = document.createElement('a');
    link.download = 'pixel-art.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
}

// submit to me

function submitPixelArt() {
    const canvas = document.getElementById("pixelart-canvas");
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("pixelart", blob, "pixelart.png");

        const response = await fetch("/submit_pixelart", {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            alert("Pixel art submitted successfully!");
        } else {
            alert("Failed to submit pixel art.");
        }
    });
}

