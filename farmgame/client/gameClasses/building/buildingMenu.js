import player from "../player/player.js";
import GVAR from "../../globalVars/global.js";
import RES from "../../resources.js";
import CVAR from "../../globalVars/const.js";
import Calc from "../../calc.js";

class BuildingMenu {
    constructor() {
        document.getElementById("close-building-menu").onclick = () => {
            this.close()
        };
        document.getElementById("building-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("building-menu-wrap"))
                this.close()
        };
        this.building = 'none';
    }
    close(){
        this.building = 'none';
        document.getElementById("building-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
    show(building) {
        this.building = building;
        const img = new Image();
        img.src = `client/assets/buildings/${building._type}/${building._type}.png`
        img.onload = function() {
            const buildingImg = document.getElementById('building-img');
            buildingImg.style.backgroundImage = `url('client/assets/buildings/${building._type}/${building._type}.png')`;
            buildingImg.style.aspectRatio = `${img.width} / ${img.height}`;
        };
        GVAR.closeAllWindows();
        document.getElementById("building-menu-wrap").style.display = "flex";
        this.renderCrafts();
    }
    renderQueue() {
        const queue = this.building._craftingItems;
        const size = this.building._slotsAmount;
        const buildingQueue = document.getElementById('building-queue');
        buildingQueue.innerHTML = '';
        for (let i = 0; i < size; i++) {
            const queueElem = document.createElement("div");
            queueElem.className = "queue-elem";
            if (queue[i] != undefined) {
                const img = document.createElement("div");
                img.className = "queue-elem-img";
                const key = Object.keys(queue[i])[0];
                img.style.backgroundImage = `url('client/assets/items/${key}.png')`;
                queueElem.appendChild(img);

                const time = document.createElement("h3");
                time.className = "queue-elem-text";
                time.innerText = Calc.formatTime(Math.trunc(queue[i].timeToFinish / 1000));
                queueElem.appendChild(time);
            }
            buildingQueue.appendChild(queueElem);
        }

        if (this.building._slotsAmount < RES.buildings[this.building._type].maxSlots + CVAR.extraSlotsCount){
            const queueElem = document.createElement("div");
            queueElem.className = "queue-elem";
            const plus = document.createElement('h3')
            plus.innerText = '+'
            plus.className = 'queue-elem-plus'
            queueElem.appendChild(plus)
            queueElem.onclick = () => {
                const extraSlotCount = this.building._slotsAmount - RES.buildings[this.building._type].maxSlots
                const price = CVAR.extraSlotPrice * Math.pow(CVAR.extraSlotCoef, extraSlotCount)
                document.getElementById('selection-menu-wrap').style.display = 'flex'
                document.getElementById('selection-text').innerText =
                `${GVAR.localization[32][GVAR.language].replace(/\{/g, Math.trunc(price / 100))}`
                document.getElementById('selection-yes').onclick = () => {
                    if (player._tokenBalance >= price){
                        this.building.incSlotsAmount()
                        player.spendToken(price)
                        this.renderQueue()
                    } else {
                        GVAR.showFloatingText(2)
                    }
                    document.getElementById('selection-menu-wrap').style.display = 'none'
                }      
            };
            buildingQueue.appendChild(queueElem);
        }
    }
    renderCrafts() {
        const type = this.building._type;
        this.renderQueue();
        const button = document.getElementById('upgrade-building');
        button.innerText = GVAR.localization[8][GVAR.language]
        if (this.building._level >= RES.buildings[type].maxLevel)
            button.remove()
        else {
            button.onclick = () => {
                document.getElementById('selection-menu-wrap').style.display = 'flex'
                document.getElementById('selection-text').innerText =
                `${GVAR.localization[33][GVAR.language].replace(/\{/g, this.building._level)}\n
                ${GVAR.localization[34][GVAR.language].replace(/\{/g, RES.buildings[type].upgradesPrice[this.building._level-1])}`
                document.getElementById('selection-yes').onclick = () => {
                    if (player._money < RES.buildings[type].upgradesPrice[this.building._level-1])
                        GVAR.showFloatingText(1)
                    else {
                        this.building.upgrade()
                        this.renderCrafts()
                        GVAR.showFloatingText(7)
                    }
                    document.getElementById('selection-menu-wrap').style.display = 'none'
                }
            };
        }
        const buildingMenuList = document.getElementById('building-menu-list');
        buildingMenuList.innerHTML = "";
        for (let product in RES.buildings[type].workTypes) {
            if (RES.buildings[type].workTypes[product].minLevel > this.building._level + 1) {
                break
            }
            const craft = document.createElement("div");
            craft.className = "craft";

            const craftImg = document.createElement("div");
            craftImg.style.backgroundImage = `url(client/assets/items/${product}.png)`;
            craftImg.className = "craft-item-image";

            const isIntersecting = (rect1, rect2) => {
                return (
                    rect1.left + rect1.width / 2 < rect2.right &&
                    rect1.right - rect1.width / 2 > rect2.left &&
                    rect1.top + rect1.height / 2 < rect2.bottom &&
                    rect1.bottom - rect1.height / 2 > rect2.top
                );
            };
            const thisMenu = this;
            const building = this.building;

            if (!building.canStartWork(RES.buildings[type].workTypes[product])) {
                craftImg.style.filter = 'grayscale(100%)'
            }
            craftImg.addEventListener('touchstart', function (e) {
                if (!player._inventory['bread']){
                    const customEvent = new Event('firstBread');
                    document.body.dispatchEvent(customEvent);
                }
                e.preventDefault();
                if (!building.canStartWork(RES.buildings[type].workTypes[product])){
                    GVAR.showFloatingText(6)
                    return
                }
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
                    if (!isIntersecting(clone.getBoundingClientRect(), craft.getBoundingClientRect()))
                        document.getElementById('drop-list').style.display = 'none';
                    const touch = event.touches[0];
                    moveAt(touch.pageX, touch.pageY);
                };
                const onTouchEnd = () => {
                    document.removeEventListener('touchmove', onTouchMove);
                    const cloneRect = clone.getBoundingClientRect();
                    const visualRect = document.getElementById('building-visual').getBoundingClientRect();
                    if (isIntersecting(cloneRect, visualRect) && building.canStartWork(RES.buildings[type].workTypes[product])) {
                        if (!player._inventory['bread']){
                            const customEvent = new Event('firstBreadStart');
                            document.body.dispatchEvent(customEvent);
                        }
                        building.startWork(RES.buildings[type].workTypes[product]);
                        thisMenu.renderCrafts();
                    } else {
                        GVAR.buildableArr.forEach(el => {
                            if (el._type == 'bakery'){
                                if (player._inventory['bread'] == undefined || (player._networth == 0 && el._craftingItems.length == 0)) {
                                    const customEvent = new Event('firstBreadBad');
                                    document.body.dispatchEvent(customEvent);
                                }
                            }
                        });
                    }
                    clone.remove();
                };

                document.addEventListener('touchmove', onTouchMove);
                document.addEventListener('touchend', onTouchEnd, { once: true });
            });

            craft.addEventListener('touchstart', (event) => {
                const dropList = document.createElement("div");
                dropList.id = 'drop-list'
                dropList.className = "craft-drop-list";
                const dropName = document.createElement("h3");  
                dropName.innerText = GVAR.localization[product].name[GVAR.language];
                dropName.className = 'drop-list-text';
                dropList.appendChild(dropName);

                const dropTime = document.createElement("h3");
                dropTime.innerText = 'time:' + Calc.formatTime(RES.buildings[type].workTypes[product].timeToFinish);
                dropTime.className = 'drop-list-text';
                dropList.appendChild(dropTime);

                let dropItems = document.createElement("div")
                dropItems.className = "drop-items-list"
                let flag = true
                for (let item in RES.buildings[type].workTypes[product].items) {
                    const dropItem = document.createElement("div");
                    if (flag) {
                        dropItems.appendChild(dropItem)
                        flag = false
                    } else {
                        dropItems.appendChild(dropItem)
                        dropList.appendChild(dropItems)
                        dropItems = document.createElement("div")
                        dropItems.className = "drop-items-list"
                        flag = true
                    }
                    dropItem.className = "drop-item";
                    const img = document.createElement("img");
                    img.src = `client/assets/items/${item}.png`;
                    img.className = 'drop-list-img';

                    const itemText = document.createElement("h3");
                    itemText.className = 'drop-items-amount';
                    let playerItemAmount = player._inventory[item];
                    const requiredItemAmount = RES.buildings[type].workTypes[product].items[item];
                    if (playerItemAmount == undefined){
                        playerItemAmount = 0
                    }
                    itemText.innerText = ` ${playerItemAmount}/${requiredItemAmount}`;

                    if (playerItemAmount < requiredItemAmount) {
                        itemText.classList.add('insufficient');
                    }
                    dropItem.appendChild(img);
                    dropItem.appendChild(itemText);
                }
                if (!flag)
                    dropList.appendChild(dropItems);
                const nowLevel = this.building._level;
                const needLevel = RES.buildings[type].workTypes[product].minLevel;
                if (nowLevel < needLevel) {
                    const newLevel = document.createElement("h3");
                    newLevel.className = 'drop-list-text';
                    newLevel.innerText = 'next level'
                    dropList.appendChild(newLevel);
                }
                const rect = craft.getBoundingClientRect();

                let topPosition = rect.bottom - rect.top;
                dropList.style.display = 'block';
                if (window.innerHeight - rect.bottom < 3 * rect.height) {
                    topPosition = -3 * rect.height;
                }

                dropList.style.top = `${topPosition}px`;
                craft.appendChild(dropList);
            });

            craft.addEventListener('touchend', (event) => {
                document.getElementById('drop-list').remove();
            });

            craft.appendChild(craftImg);

            buildingMenuList.appendChild(craft);
        }
    }
}
export const buildingMenu = new BuildingMenu();
