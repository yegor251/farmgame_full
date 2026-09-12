import player from "../player/player.js";
import socketClient from "../../init.js";
import RES from "../../resources.js";
import GVAR from "../../globalVars/global.js";
import Calc from "../../calc.js";

class BoosterMenu{
    constructor() {
        document.getElementById("close-booster-menu").onclick = () => {
            this.close()
        }
        document.getElementById("booster").onclick = () => {
            this.show()
        }
        document.getElementById("booster-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("booster-menu-wrap"))
                this.close()
        };
    }
    show(){
        GVAR.closeAllWindows();
        document.getElementById("booster-menu-wrap").style.display = "flex";
        this.drawMenu();
        this.interval = setInterval(() => {
            this.renderActivBoosters()
        }, 1000);

    }
    close() {
        document.getElementById("booster-menu-wrap").style.display = "none";
        document.getElementById("main-menu-wrap").style.display = "flex";
        clearInterval(this.interval)
    }
    renderActivBoosters(){
        const activBoosters = document.getElementById('activ-boosters');
        activBoosters.innerHTML = ''
        for (let i = 0; i < 4; i++) {
            const activBooster = document.createElement('div')
            activBooster.className = 'activ-booster'
            if (i < player._activBoostersArr.length) {
                const img = document.createElement('div')
                img.className = 'activ-booster-img'
                img.style.backgroundImage = `url(client/assets/design/${player._activBoostersArr[i].type}.png)`
                const timer = document.createElement('h3')
                const str = Calc.formatTime(Math.floor((player._activBoostersArr[i].timeStamp - Date.now()) / 1000))
                let hIndex = str.indexOf('h');
                let mIndex = str.indexOf('m', hIndex);
                if (hIndex !== -1) {
                    timer.innerText = mIndex !== -1 ? str.substring(0, mIndex + 1) : str.substring(0, hIndex + 1);
                } else {
                    timer.innerText = str
                }
                timer.className = 'activ-booster-timer'
                const timerContent = document.createElement('div')
                timerContent.className = 'activ-booster-timer-content'
                timerContent.appendChild(timer)
                const amount = document.createElement('h3')
                amount.innerText = player._activBoostersArr[i].boosterAmount; 
                amount.className = 'activ-booster-amount'
                const amountContent = document.createElement('div')
                amountContent.className = 'activ-booster-amount-content'
                amountContent.appendChild(amount)

                activBooster.appendChild(img)
                activBooster.appendChild(amountContent)
                activBooster.appendChild(timerContent)
            }
            activBoosters.appendChild(activBooster)
        }
    }
    drawMenu() {
        this.renderActivBoosters();
        const list = document.getElementById('boosters-list');
        list.innerHTML = '';
        let shelf = null;
        const boostersOnShelf = 4
        for (let i = 0; i < player._boostersArr.length; i++) {
            if (i % boostersOnShelf == 0){
                shelf = document.createElement('div')
                shelf.className = 'booster-shelf'
                list.appendChild(shelf)
            }

            const booster = player._boostersArr[i];
            const boostDiv = document.createElement('div');
            boostDiv.className = 'booster'

            const amount = document.createElement('h3');
            amount.innerText = 'x' + booster.amount;
            amount.className = 'booster-amount'
            boostDiv.appendChild(amount);
    
            const img = document.createElement('div');
            img.className = 'booster-img'
            img.style.backgroundImage = `url(client/assets/design/${booster.type}.png)`
            boostDiv.appendChild(img);
            shelf.appendChild(boostDiv);

            const isIntersecting = (rect1, rect2) => {
                return (
                    rect1.left + rect1.width / 2 < rect2.right &&
                    rect1.right - rect1.width / 2 > rect2.left &&
                    rect1.top + rect1.height / 2 < rect2.bottom &&
                    rect1.bottom - rect1.height / 2 > rect2.top
                );
            };
            const menu = this
            img.addEventListener('touchstart', function (e) {
                e.preventDefault();
                const clone = this.cloneNode(true);

                clone.classList.add('clone-image');
                document.body.appendChild(clone);

                const computedStyle = window.getComputedStyle(this);
                clone.style.width = computedStyle.width;
                clone.style.height = computedStyle.height;

                const moveAt = (pageX, pageY) => {
                    clone.style.left = pageX - clone.offsetWidth / 2 + 'px';
                    clone.style.top = pageY - clone.offsetHeight / 2 + 'px';
                };

                const touch = e.touches[0];
                moveAt(touch.pageX, touch.pageY);

                const onTouchMove = (event) => {
                    if (!isIntersecting(clone.getBoundingClientRect(), img.getBoundingClientRect()))
                        document.getElementById('drop-list').style.display = 'none';
                    const touch = event.touches[0];
                    moveAt(touch.pageX, touch.pageY);
                };
                const onTouchEnd = () => {
                    document.removeEventListener('touchmove', onTouchMove);
                    const cloneRect = clone.getBoundingClientRect();
                    const visualRect = document.getElementById('activ-boosters').getBoundingClientRect();
                    if (isIntersecting(cloneRect, visualRect)) {
                        if (!player.canActivateBooster(i)){
                            GVAR.showFloatingText(5)
                        } else {
                            player.activateBooster(i)
                            socketClient.send(`activateb/${i}`)
                            if (booster.type == 'WorkSpeed'){
                                GVAR.buildableArr.forEach(el => {
                                    if (RES.buildingNames.bakery.includes(el._type) || RES.buildingNames.animalPen.includes(el._type)){
                                        el.activateBooster()
                                    }
                                });
                            } else if (booster.type == 'GrowSpeed'){
                                GVAR.buildableArr.forEach(el => {
                                    if (el._type=="garden" || RES.buildingNames.bush.includes(el._type)){
                                        el.activateBooster()
                                    }
                                });
                            }
                            socketClient.send(`regen`)
                            menu.renderActivBoosters()
                            menu.drawMenu()
                        }
                    }
                    clone.remove();
                };

                document.addEventListener('touchmove', onTouchMove);
                document.addEventListener('touchend', onTouchEnd, { once: true });
            });

            img.addEventListener('touchstart', (event) => {
                const dropList = document.createElement("div");
                dropList.id = 'drop-list'
                dropList.className = "craft-drop-list";
                const dropName = document.createElement("h3");
                dropName.innerText = booster.type;
                dropName.className = 'drop-list-text';
                dropList.appendChild(dropName);

                const dropTime = document.createElement("h3");
                dropTime.innerText = 'time:' + Calc.formatTime(booster.time);
                dropTime.className = 'drop-list-text';
                dropList.appendChild(dropTime);

                img.appendChild(dropList);
                dropList.style.display = 'block';

                const rect = img.getBoundingClientRect();

                let topPosition = rect.bottom - rect.top;

                dropList.style.top = `${topPosition}px`;
            });

            img.addEventListener('touchend', () => {
                document.getElementById('drop-list').remove();
            });
        }
        let i = player._boostersArr.length / boostersOnShelf;
        while (i <= 1){
            shelf = document.createElement('div')
            shelf.className = 'booster-shelf'
            list.appendChild(shelf)
            i += 1
        }
    }
    
}
const boosterMenu = new BoosterMenu();
export default boosterMenu;
