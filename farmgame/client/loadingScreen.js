import CVAR from "./globalVars/const.js";

class WebsiteLoader {
  constructor() {
    this.loadingText = document.getElementById('loading-text');
    this.loadingBar = document.getElementById('loading-bar');
    this.progress = 0
    this.interval = setInterval(() => {
      if (this.progress<25)
        this.updateLoading(this.progress + 1, 'Loading')
      else
        clearInterval(this.interval)
    }, 100);
  }

  // Function to update loading text and percentage from outside
  updateLoading(progress, text) {
    this.loadingText.innerText = text;
    this.loadingBar.style.width = `${Math.min(100, progress)}%`;
    this.progress = progress
  }

  // Function to hide loading screen
  hideLoadingScreen() {
    const loadingContainer = document.getElementById('loading-container');
    const mainContent = document.getElementById('main-content');
    loadingContainer.style.display = 'none';
    mainContent.style.display = 'none';
    // window.Telegram.WebApp.requestFullscreen();
    setTimeout(() => {
      CVAR.minScale = 5 * window.innerHeight / 1000; CVAR.maxScale = 15 * window.innerHeight / 1000;
    }, 200);
  }
}

// Function to start the background animations (immediate, without delays)
function startAnimations() {
  document.querySelector('#birds img').style.bottom = '0';
  document.querySelector('#clouds img').style.bottom = '0';
  document.querySelector('#stars img').style.bottom = '0';
  
  // Clone and loop images to ensure smooth scrolling
  const birds = document.querySelector('#birds');
  const clouds = document.querySelector('#clouds');
  const stars = document.querySelector('#stars');

  // Function to clone the image for continuous animation
  function cloneLayer(layer) {
    const img = layer.querySelector('img');
    const clone = img.cloneNode(true);
    clone.style.left = '100%';
    layer.appendChild(clone);
  }

  // Clone the images to make them loop
  cloneLayer(birds);
  cloneLayer(clouds);
  cloneLayer(stars);
}

const loader = new WebsiteLoader();
export default loader;

startAnimations()
