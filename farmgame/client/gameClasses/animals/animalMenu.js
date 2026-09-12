import Calc from "../../calc.js";
import GVAR from "../../globalVars/global.js";
import RES from "../../resources.js";
import player from "../player/player.js";

class AnimalMenu{
    constructor() {
        document.getElementById("close-animal-menu").onclick = () => {
            this.close()
        }
        document.getElementById("animal-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("animal-menu-wrap"))
                this.close()
        };
        this.animalPen = 'none'
    }
    close(){
        document.getElementById("animal-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
        this.animalPen = 'none'
        let startButton = document.getElementById('animal-start-button');
        let newButton = startButton.cloneNode(true);
        startButton.parentNode.replaceChild(newButton, startButton);
        startButton = newButton;
        startButton.dataset.handlerAdded = undefined
    }
    show(animalPen){
        this.animalPen = animalPen
        const animalImg = document.getElementById('animal-img')
        animalImg.style.backgroundImage = `url(${animalPen._image.src})`;
        animalImg.style.aspectRatio = `${animalPen._image.width} / ${animalPen._image.height}`
        GVAR.closeAllWindows()
        document.getElementById("animal-menu-wrap").style.display = "flex";
        document.getElementById('animal-pen-name').innerText = RES.buildings[animalPen._type].localization.name[GVAR.language]
        const startButton = document.getElementById("animal-start-button");
        const feedType = Object.keys(RES.buildings[animalPen._type].intake)[0]
        startButton.style.backgroundImage = `url(client/assets/items/${feedType}.png)`
        const upgradeButton = document.getElementById('animal-upgrade');
        upgradeButton.innerText = GVAR.localization[8][GVAR.language];
        const amountText = document.getElementById("feed-amount")
        if (!player._inventory[feedType])
            player._inventory[feedType] = 0
        amountText.innerText = `${player._inventory[feedType]}/${animalPen._animals.length}`
        if (player._inventory[feedType] >= animalPen._animals.length && animalPen._animals.length!= 0)
            amountText.className = 'unlocked'
        else
            amountText.className = 'locked'
        this.renderMenu()
    }
    renderTimer(){
        if (this.animalPen._timeToFinish == 0){
            this.close()
            return
        }
        const textTime = document.getElementById("animal-timeToFinish")
        if (!this.animalPen._timeToFinish)
            textTime.innerText = '-'
        else
            textTime.innerText = Calc.formatTime(Math.floor(this.animalPen._timeToFinish / 1000))
        
        let remainingTime = 0;
        let totalTime = this.animalPen._timeStamp;
        if (this.animalPen._timeToFinish == undefined)
            remainingTime = totalTime;
        else
            remainingTime = this.animalPen._timeToFinish

        var progressLine = document.getElementById('animal-process-line');
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
        const type = this.animalPen._type;
        this.renderTimer();
        const animalPen = this.animalPen;
        const upgradeButton = document.getElementById('animal-upgrade');
        upgradeButton.innerText = GVAR.localization[8][GVAR.language]
        if (this.animalPen._level >= RES.buildings[type].maxLevel)
            upgradeButton.remove()
        else {
            upgradeButton.onclick = () => {
                document.getElementById('selection-menu-wrap').style.display = 'flex'
                document.getElementById('selection-text').innerText =
                `${GVAR.localization[30][GVAR.language].replace(/\{/g, (animalPen._level-1)*10)}\n
                ${GVAR.localization[31][GVAR.language].replace(/\{/g, RES.buildings[type].upgradesPrice[this.animalPen._level-1])}`
                document.getElementById('selection-yes').onclick = () => {
                    if (player._money < RES.buildings[type].upgradesPrice[this.animalPen._level-1])
                        GVAR.showFloatingText(1)
                    else {
                        this.animalPen.upgrade()
                        GVAR.showFloatingText(7)
                    }
                    document.getElementById('selection-menu-wrap').style.display = 'none'
                }
            };
        }
    
        const isIntersecting = (rect1, rect2) => {
            return (
                rect1.left + rect1.width / 2 < rect2.right &&
                rect1.right - rect1.width / 2 > rect2.left &&
                rect1.top + rect1.height / 2 < rect2.bottom &&
                rect1.bottom - rect1.height / 2 > rect2.top
            );
        };
    
        const startButton = document.getElementById("animal-start-button");
        const feedType = Object.keys(RES.buildings[type].intake)[0]
        startButton.style.backgroundImage = `url(client/assets/items/${feedType}.png)`;
        if (this.animalPen.canStartWork()) {
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
    
            const onTouchMove = (event) => {
                const touch = event.touches[0];
                moveAt(touch.pageX, touch.pageY);
            };
    
            const onTouchEnd = () => {
                document.removeEventListener('touchmove', onTouchMove);
                const cloneRect = clone.getBoundingClientRect();
                const imgRect = document.getElementById('animal-img').getBoundingClientRect();
                if (isIntersecting(cloneRect, imgRect) && animalPen.canStartWork()) {
                    animalPen.startWork();
                    startButton.style.filter = 'grayscale(100%)';
                    startButton.removeEventListener('touchstart', startButtonTouchStartHandler);
                    startButton.dataset.handlerAdded = 'false';
                }
                clone.remove();
            };
    
            document.addEventListener('touchmove', onTouchMove);
            document.addEventListener('touchend', onTouchEnd, { once: true });
        }
    }    
}
export const animalMenu = new AnimalMenu();