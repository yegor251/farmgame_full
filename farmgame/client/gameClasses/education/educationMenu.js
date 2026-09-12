import shop from "../shop/shop.js";
import GVAR from "../../globalVars/global.js";
import player from "../player/player.js";
import { fieldMenu } from "../field/fieldMenu.js";
import { buildingMenu } from "../building/buildingMenu.js";
import { spin } from "../spin/spin.js";
import { orderManager } from "../orders/orders.js";
import Calc from "../../calc.js";
import camera from "../controller/camera.js";
import CVAR from "../../globalVars/const.js";

const stages = [
    {
        getZone: () => ({
            x: (document.getElementById('open-shop').getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementById('open-shop').getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementById('open-shop').getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementById('open-shop').getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'click',
        getCondition: () => {return GVAR.countBuilding('garden') == 0},
        text: GVAR.localization[37][GVAR.language],
        text_pos: {x: 0, y: 35}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('shop-item')[0].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('shop-item')[0].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('shop-item')[0].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('shop-item')[0].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'firstGarden',
        getCondition: () => (GVAR.countBuilding('garden') == 0),
        text: GVAR.localization[38][GVAR.language],
        text_pos: {x: 35, y: 15}
    },
    {
        getZone: () => ({}),
        event: 'firstGardenPlace',
        getCondition: () => (GVAR.countBuilding('garden') == 0),
        text: GVAR.localization[39][GVAR.language],
        text_pos: {x: 3, y: 80}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('plant-craft')[0].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('plant-craft')[0].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('plant-craft')[0].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('plant-craft')[0].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'firstPlant',
        getCondition: () => (player._inventory['wheat'] == 4 && GVAR.countBuilding('bakery') == 0),
        text: GVAR.localization[40][GVAR.language],
        text_pos: {x: 0, y: 65}
    },
    {
        getZone: () => ({}),
        event: 'firstPlantDone',
        getCondition: () => (player._inventory['wheat'] == 4 && GVAR.countBuilding('bakery') == 0),
        text: GVAR.localization[41][GVAR.language],
        text_pos: {x: 0, y: 30}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('shop-item')[1].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('shop-item')[1].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('shop-item')[1].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('shop-item')[1].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'firstBuilding',
        getCondition: () => (GVAR.countBuilding('bakery') == 0),
        text: GVAR.localization[42][GVAR.language],
        text_pos: {x: 30, y: 50}
    },
    {
        getZone: () => ({}),
        event: 'firstBuildingPlace',
        getCondition: () => (GVAR.countBuilding('bakery') == 0),
        text: GVAR.localization[43][GVAR.language],
        text_pos: {x: 3, y: 80}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('craft')[0].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('craft')[0].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('craft')[0].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('craft')[0].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'firstBread',
        getCondition: () => {
            if (GVAR.countBuilding('bakery') == 1 && player._networth == 0) {
                for (let i = 0; i < GVAR.buildableArr.length; i++) {
                    const el = GVAR.buildableArr[i];
                    if (el._type == "bakery"){
                        if (!player._inventory['bread'] && el._craftingItems.length == 0){
                            return true
                        } else {
                            return false
                        }
                    }
                }
            }
        },
        text: GVAR.localization[44][GVAR.language],
        text_pos: {x: 10, y: 30}
    },
    {
        getZone: () => ({}),
        event: 'firstBreadStart',
        getCondition: () => {
            if (GVAR.countBuilding('bakery') == 1 && player._networth == 0) {
                for (let i = 0; i < GVAR.buildableArr.length; i++) {
                    const el = GVAR.buildableArr[i];
                    if (el._type == "bakery"){
                        if (!player._inventory['bread'] && el._craftingItems.length == 0){
                            return true
                        } else {
                            return false
                        }
                    }
                }
            }
        },
        text: GVAR.localization[45][GVAR.language],
        text_pos: {x: 10, y: 45}
    },
    {
        getZone: () => ({
            x: (document.getElementById('spin-button').getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementById('spin-button').getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementById('spin-button').getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementById('spin-button').getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'click',
        getCondition: () => (false),
        text: GVAR.localization[46][GVAR.language],
        text_pos: {x: 10, y: 80}
    },
    {
        getZone: () => ({}),
        event: 'firstBreadWait',
        getCondition: () => (false),
        text: '',
        text_pos: {x: 0, y: 0}
    },
    {
        getZone: () => {
            for (let i = 0; i < GVAR.buildableArr.length; i++) {
                const el = GVAR.buildableArr[i];
                if (el._type == 'bakery'){
                    const pos1 = Calc.worldToScreen(el._x, el._y, camera.getPos(), GVAR.scale)
                    const pos2 = Calc.worldToScreen(el._x + el._w, el._y + el._h, camera.getPos(), GVAR.scale)
                    const r = {
                        x: (pos1.x / window.innerWidth) * 100,
                        y: (pos1.y / window.innerHeight) * 100,
                        w: ((pos2.x - pos1.x) / window.innerWidth) * 100,
                        h: ((pos2.y - pos1.y) / window.innerHeight) * 100,
                    }
                    return r
                }
            }
        },
        event: 'click',
        getCondition: () => (false),
        text: GVAR.localization[68][GVAR.language],
        text_pos: {x: 10, y: 50}
    },
    {
        getZone: () => ({}),
        event: 'firstBreadDone',
        getCondition: () => (player._networth == 0 && !player._inventory['bread']),
        text: '',
        text_pos: {x: 0, y: 0}
    },
    {
        getZone: () => {
            for (let i = 0; i < GVAR.buildableArr.length; i++) {
                const el = GVAR.buildableArr[i];
                if (el._type == 'orders_board'){
                    const pos1 = Calc.worldToScreen(el._x, el._y, camera.getPos(), GVAR.scale)
                    const pos2 = Calc.worldToScreen(el._x + el._w, el._y + el._h, camera.getPos(), GVAR.scale)
                    const r = {
                        x: (pos1.x / window.innerWidth) * 100,
                        y: (pos1.y / window.innerHeight) * 100,
                        w: ((pos2.x - pos1.x) / window.innerWidth) * 100,
                        h: ((pos2.y - pos1.y) / window.innerHeight) * 100,
                    }
                    return r
                }
            }
        },
        event: 'click',
        getCondition: () => (player._networth == 0 && player._inventory['bread']),
        text: GVAR.localization[67][GVAR.language],
        text_pos: {x: 10, y: 12}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('order')[0].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('order')[0].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('order')[0].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('order')[0].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'click',
        getCondition: () => (player._networth == 0 && player._inventory['bread']),
        text: GVAR.localization[47][GVAR.language],
        text_pos: {x: 10, y: 12}
    },
    {
        getZone: () => ({
            x: (document.getElementsByClassName('complete-order')[0].getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementsByClassName('complete-order')[0].getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementsByClassName('complete-order')[0].getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementsByClassName('complete-order')[0].getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'click',
        getCondition: () => (player._networth == 0 && player._inventory['bread']),
        text: GVAR.localization[48][GVAR.language],
        text_pos: {x: 10, y: 12}
    },
    {
        getZone: () => {
            for (let i = 0; i < GVAR.buildableArr.length; i++) {
                const el = GVAR.buildableArr[i];
                if (el._type == 'barn'){
                    const pos1 = Calc.worldToScreen(el._x, el._y, camera.getPos(), GVAR.scale)
                    const pos2 = Calc.worldToScreen(el._x + el._w, el._y + el._h, camera.getPos(), GVAR.scale)
                    const r = {
                        x: (pos1.x / window.innerWidth) * 100,
                        y: (pos1.y / window.innerHeight) * 100,
                        w: ((pos2.x - pos1.x) / window.innerWidth) * 100,
                        h: ((pos2.y - pos1.y) / window.innerHeight) * 100,
                    }
                    return r
                }
            }
        },
        event: 'click',
        getCondition: () => (false),
        text: GVAR.localization[69][GVAR.language],
        text_pos: {x: 10, y: 50}
    },
    {
        getZone: () => ({
            x: (document.getElementById('stash').getBoundingClientRect().left / window.innerWidth) * 100,
            y: (document.getElementById('stash').getBoundingClientRect().top / window.innerHeight) * 100,
            w: (document.getElementById('stash').getBoundingClientRect().width / window.innerWidth) * 100,
            h: (document.getElementById('stash').getBoundingClientRect().height / window.innerHeight) * 100
        }),
        event: 'click',
        getCondition: () => (false),
        text: GVAR.localization[70][GVAR.language],
        text_pos: {x: 10, y: 10}
    }
]


class EducationMenu {
    constructor() {
    }
    start(){
        for (let i = 0; i < stages.length; i++) {
            this.currentStage = i;
            if (stages[i].getCondition())
                break
        }
        if (this.currentStage == stages.length-1 && !stages[stages.length-1].getCondition())
            this.currentStage = stages.length
        if (this.currentStage > 12)
            GVAR.canRerollOrders = true
        if (this.currentStage < 6)
            document.getElementById('shop-list').style.overflowY = 'hidden'
        if (this.currentStage == 3)
            GVAR.buildableArr.forEach(el => {
                if (el._type == 'garden')
                    fieldMenu.show(el)
            });
        else if (this.currentStage == 7)
            GVAR.buildableArr.forEach(el => {
                if (el._type == 'bakery')
                    buildingMenu.show(el)
            });
        else if (this.currentStage == 9)
            spin.show()
        else if (this.currentStage == 5)
            shop.show()
        else if (this.currentStage == 14)
            orderManager.show()
        this.gardenBadFlag = true
        this.plantBadFlag = true
        this.breadBadFlag = true
        this.show();
    }
    async show() {
        this.updateStage(this.currentStage);
    }
    async updateStage(stageNumber) {
        const stage = stages[stageNumber];
        if (!stage) 
            return;
        this.createZone(stage);
    
        const handleEventClick = async (e) => {
            const targetElement = document.getElementById('avtiv_zone');
            const rect = targetElement.getBoundingClientRect();
    
            if (e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom) {
                document.body.removeEventListener(stage.event, handleEventClick);

                if (stageNumber == 13){ // номер события где клик по области экрана где ордера
                    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
                    await sleep(100);
                } else if (stageNumber == 15) {
                    GVAR.closeAllWindows()
                    for (let i = 0; i < GVAR.buildableArr.length; i++) {
                        const el = GVAR.buildableArr[i];
                        if (el._type == 'barn'){
                            camera._x = (el._x - CVAR.tileSide) * GVAR.scale
                            camera._y = (el._y - 2 * CVAR.tileSide) * GVAR.scale
                            camera.updateBoundingBox();
                        }
                    }
                } else if (stageNumber == 16) {
                    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
                    await sleep(100);
                } else if (stageNumber == 17) {
                    GVAR.showFloatingText(71)
                }
                this.nextStage();
            }
        };

        const handleEventFirstGarden = (e) => {
            document.body.removeEventListener(stage.event, handleEventFirstGarden);
            this.nextStage();
        };

        const handleEventFirstGardenPlace = (e) => {
            if (this.gardenBadFlag){
                this.gardenBadFlag = false
                GVAR.buildableArr.forEach(el => {
                    if (el._type == 'garden')
                        fieldMenu.show(el)
                });
                this.nextStage();
            }
            document.body.removeEventListener(stage.event, handleEventFirstGardenPlace);
        };

        const handleEventFirstGardenPlaceBad = (e) => {
            document.body.removeEventListener('firstGardenPlaceBad', handleEventFirstGardenPlaceBad);
            this.currentStage -= 2
            shop.show()
            this.nextStage();
        };

        const handleEventFirstPlant = (e) => {    
            this.nextStage();
            document.body.removeEventListener(stage.event, handleEventFirstPlant);
        };

        const handleEventFirstPlantDone = async (e) => {
            if (this.plantBadFlag){
                this.plantBadFlag = false
                const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
                await sleep(500);
                fieldMenu.close()
                shop.show()
                this.nextStage();
            }
            document.body.removeEventListener(stage.event, handleEventFirstPlantDone);
        };

        const handleEventFirstPlantBad = (e) => {
            document.body.removeEventListener('firstPlantBad', handleEventFirstPlantBad);
            this.currentStage -= 2
            this.nextStage();
        };

        const handleEventFirstBuilding = (e) => {
            document.body.removeEventListener(stage.event, handleEventFirstBuilding);
            this.nextStage();
        };

        const handleEventFirstBuildingPlace = (e) => {
            document.body.removeEventListener(stage.event, handleEventFirstBuildingPlace);
            GVAR.buildableArr.forEach(el => {
                if (el._type == 'bakery')
                    buildingMenu.show(el)
            });
            document.getElementById('shop-list').style.overflowY = 'auto'
            this.nextStage();
        };

        const handleEventFirstBuildingPlaceBad = (e) => {
            document.body.removeEventListener('firstBuildingPlaceBad', handleEventFirstBuildingPlaceBad);
            shop.show()
            this.currentStage -= 2
            this.nextStage();
        };

        const handleEventFirstBread = (e) => {
            document.body.removeEventListener('firstBread', handleEventFirstBread);
            this.nextStage();
        };

        const handleEventFirstBreadStart = async (e) => {
            if (this.breadBadFlag){
                this.breadBadFlag = false
                const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
                await sleep(1000);
                buildingMenu.close()
                spin.show()
                this.nextStage();
            }
            document.body.removeEventListener('firstBreadStart', handleEventFirstBreadStart);
        };

        const handleEventFirstBreadBad = (e) => {
            document.body.removeEventListener('firstBreadBad', handleEventFirstBreadBad);
            this.currentStage -= 2
            this.nextStage();
        };

        const handleEventFirstBreadDone = (e) => {
            document.body.removeEventListener('firstBreadDone', handleEventFirstBreadDone);
            for (let i = 0; i < GVAR.buildableArr.length; i++) {
                const el = GVAR.buildableArr[i];
                if (el._type == 'orders_board'){
                    camera._x = (el._x - CVAR.tileSide) * GVAR.scale
                    camera._y = (el._y - 2 * CVAR.tileSide) * GVAR.scale
                    camera.updateBoundingBox();
                }
            }
            this.nextStage();
        };

        const handleEventfirstBreadWait = (e) => {
            document.body.removeEventListener('firstBreadWait', handleEventfirstBreadWait);
            GVAR.closeAllWindows()
            for (let i = 0; i < GVAR.buildableArr.length; i++) {
                const el = GVAR.buildableArr[i];
                if (el._type == 'bakery'){
                    camera._x = (el._x - CVAR.tileSide) * GVAR.scale
                    camera._y = (el._y - 2 * CVAR.tileSide) * GVAR.scale
                    camera.updateBoundingBox();
                }
            }
            this.nextStage();
        };

    
        if (stage.event === 'firstGarden') {
            document.body.addEventListener(stage.event, handleEventFirstGarden);
        } else if (stage.event === 'firstGardenPlace'){
            document.body.addEventListener(stage.event, handleEventFirstGardenPlace);
            document.body.addEventListener('firstGardenPlaceBad', handleEventFirstGardenPlaceBad);
        } else if (stage.event === 'click') {
            document.body.addEventListener(stage.event, handleEventClick);
        } else if (stage.event === 'firstPlant') {
            document.body.addEventListener(stage.event, handleEventFirstPlant);
        } else if (stage.event === 'firstPlantDone') {
            document.body.addEventListener(stage.event, handleEventFirstPlantDone);
            document.body.addEventListener('firstPlantBad', handleEventFirstPlantBad);
        } else if (stage.event === 'firstBuilding') {
            document.body.addEventListener(stage.event, handleEventFirstBuilding);
        } else if (stage.event === 'firstBuildingPlace') {
            document.body.addEventListener(stage.event, handleEventFirstBuildingPlace);
            document.body.addEventListener('firstBuildingPlaceBad', handleEventFirstBuildingPlaceBad);
        } else if (stage.event === 'firstBread') {
            const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
            await sleep(10);
            this.createZone(stage)
            document.body.addEventListener(stage.event, handleEventFirstBread);
        } else if (stage.event === 'firstBreadStart') {
            document.body.addEventListener(stage.event, handleEventFirstBreadStart);
            document.body.addEventListener('firstBreadBad', handleEventFirstBreadBad);
        } else if (stage.event === 'firstBreadDone') {
            document.body.addEventListener(stage.event, handleEventFirstBreadDone);
        } else if (stage.event === 'firstBreadWait') {
            document.body.addEventListener(stage.event, handleEventfirstBreadWait);
        }
        
        document.getElementById('education-menu-wrap').style.display = 'flex';
    }    
    nextStage() {
        document.getElementById('education-menu-wrap').style.display = 'none';
        this.currentStage += 1;
        this.updateStage(this.currentStage);
    }
    createZone(stage) {
        const el = stage.getZone()
        const block1 = document.createElement('div');
        block1.className = 'education-unactiv-zone';
        block1.style.left = '0';
        block1.style.top = '0';
        block1.style.width = '100vw';
        block1.style.height = `${el.y}vh`;
    
        const block2 = document.createElement('div');
        block2.className = 'education-unactiv-zone';
        block2.style.left = '0';
        block2.style.top = `${el.y}vh`;
        block2.style.width = `${el.x}vw`;
        block2.style.height = `${el.h}vh`;
    
        const block3 = document.createElement('div');
        block3.className = 'education-unactiv-zone';
        block3.style.left = `${el.x + el.w}vw`;
        block3.style.top = `${el.y}vh`;
        block3.style.width = `${100 - el.x - el.w}vw`;
        block3.style.height = `${el.h}vh`;
    
        const block4 = document.createElement('div');
        block4.className = 'education-unactiv-zone';
        block4.style.left = '0';
        block4.style.top = `${el.y + el.h}vh`;
        block4.style.width = '100vw';
        block4.style.height = `${100 - el.y - el.h}vh`;
    
        const block5 = document.createElement('div');
        block5.className = 'education-activ-zone';
        block5.style.left = `${el.x}vw`;
        block5.style.top = `${el.y}vh`;
        block5.style.width = `${el.w}vw`;
        block5.style.height = `${el.h}vh`;
        block5.id = 'avtiv_zone'

        const text = document.createElement('h3')
        text.className = 'education-text'
        text.innerText = stage.text
        text.style.left = `${stage.text_pos.x}vw`
        text.style.top = `${stage.text_pos.y}vh`
        
        document.getElementById('education-menu-wrap').innerHTML = '';
        document.getElementById('education-menu-wrap').appendChild(block1);
        document.getElementById('education-menu-wrap').appendChild(block2);
        document.getElementById('education-menu-wrap').appendChild(block3);
        document.getElementById('education-menu-wrap').appendChild(block4);
        document.getElementById('education-menu-wrap').appendChild(block5);
        document.getElementById('education-menu-wrap').appendChild(text)
    }    
    close(){
        document.getElementById("education-menu-wrap").remove();
    }
}

export const educationMenu = new EducationMenu();