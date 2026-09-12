import Calc from "../../calc.js";
import GVAR from "../../globalVars/global.js";
import RES from "../../resources.js";
import player from "../player/player.js";

class BushMenu{
    constructor() {
        document.getElementById("close-bush-menu").onclick = () => {
            this.close()
        }
        document.getElementById("bush-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("bush-menu-wrap"))
                this.close()
        };
        this.bush = 'none'
    }
    close(){
        document.getElementById("bush-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
        this.bush = 'none'
        let startButton = document.getElementById('bush-reset');
        let newButton = startButton.cloneNode(true);
        startButton.parentNode.replaceChild(newButton, startButton);
        startButton = newButton;
        startButton.dataset.handlerAdded = undefined
    }
    show(bush){
        this.bush = bush
        GVAR.closeAllWindows()
        document.getElementById("bush-name").innerText = RES.buildings[bush._type].localization.name[GVAR.language]
        document.getElementById("bush-menu-wrap").style.display = "flex";
        this.renderMenu()
    }
    renderTimer(){
        if (this.bush._timeToFinish == 0){
            this.close()
            return
        }
        const textTime = document.getElementById("bush-timeToFinish")
        if (this.bush._timeToFinish == undefined)
            textTime.innerText = '-'
        else
            textTime.innerText = Calc.formatTime(Math.floor(this.bush._timeToFinish / 1000))
        
        let remainingTime = 0;
        let totalTime = this.bush._timeStamp;
        if (this.bush._timeToFinish == undefined)
            remainingTime = totalTime;
        else
            remainingTime = this.bush._timeToFinish

        const bushImage = document.getElementById('bush-img');
        bushImage.style.backgroundImage = `url(${this.bush._image.src})`
        bushImage.style.aspectRatio = `${this.bush._image.width} / ${this.bush._image.height}`

        var progressLine = document.getElementById('bush-process-line');
        var progressBar = progressLine.querySelector('.progress');
        
        if (!progressBar) {
            progressBar = document.createElement('div');
            progressBar.className = 'progress';
            progressLine.appendChild(progressBar);
        }
        
        var percentage = ((totalTime - remainingTime) / totalTime) * 100;
        
        percentage = Math.max(0, Math.min(100, percentage));
        progressBar.style.transition = 'width 0.5s ease';
        progressBar.style.width = percentage + '%';
    }
    renderMenu() {
        this.renderTimer();
    
        const isIntersecting = (rect1, rect2) => {
            return (
                rect1.left + rect1.width / 2 < rect2.right &&
                rect1.right - rect1.width / 2 > rect2.left &&
                rect1.top + rect1.height / 2 < rect2.bottom &&
                rect1.bottom - rect1.height / 2 > rect2.top
            );
        };
    
        const bush = this.bush;
        const startButton = document.getElementById("bush-reset");
        startButton.style.backgroundImage = `url(client/assets/design/waterer1.png)`;

        const resetPrice = document.getElementById("bush-reset-price");
        if (bush._collectedAmount < bush._collectedAmountLimit){
            resetPrice.innerText = ''
        } else{
            resetPrice.innerText = bush._resetPrice
        }

        if (this.bush.canReset()) {
            if (startButton.dataset.handlerAdded !== 'true') {
                startButton.style.filter = 'grayscale(0%)';
                startButton.addEventListener('touchstart', startButtonTouchStartHandler);
                startButton.dataset.handlerAdded = 'true';
            }
        }else {
            startButton.style.filter = 'grayscale(100%)';
            startButton.removeEventListener('touchstart', startButtonTouchStartHandler);
            startButton.dataset.handlerAdded = 'false';
        }
    
        function startButtonTouchStartHandler(e) {
            e.preventDefault();
            const clone = this.cloneNode(true);
            clone.classList.add('clone-image');
            document.body.appendChild(clone);
    
            const moveAt = (pageX, pageY) => {
                clone.style.left = pageX - clone.offsetWidth / 2 + 'px';
                clone.style.top = pageY - clone.offsetHeight / 2 + 'px';
            };
    
            const touch = e.touches[0];
            moveAt(touch.pageX, touch.pageY);
    
            let currentImage = '';
            const onTouchMove = (event) => {
                const touch = event.touches[0];
                moveAt(touch.pageX, touch.pageY);
                const cloneRect = clone.getBoundingClientRect();
                const imgRect = document.getElementById('bush-img').getBoundingClientRect();
                const newImage = isIntersecting(cloneRect, imgRect) 
                                ? 'url(client/assets/design/waterer2.png)' 
                                : 'url(client/assets/design/waterer1.png)';
                if (currentImage !== newImage) {
                    currentImage = newImage;
                    clone.style.backgroundImage = newImage;
                }
            };
    
            const onTouchEnd = () => {
                document.removeEventListener('touchmove', onTouchMove);
                const cloneRect = clone.getBoundingClientRect();
                const imgRect = document.getElementById('bush-img').getBoundingClientRect();
                if (isIntersecting(cloneRect, imgRect)) {
                    if (player._money >= bush._resetPrice) {
                        bush.reset();
                        startButton.style.filter = 'grayscale(100%)';
                        startButton.removeEventListener('touchstart', startButtonTouchStartHandler);
                        startButton.dataset.handlerAdded = 'false';
                    } else {
                        GVAR.showFloatingText(1)
                    }
                }
                clone.remove();
            };
    
            document.addEventListener('touchmove', onTouchMove);
            document.addEventListener('touchend', onTouchEnd, { once: true });
        }
    }    
}
export const bushMenu = new BushMenu();