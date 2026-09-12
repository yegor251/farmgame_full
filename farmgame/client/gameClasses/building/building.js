import GVAR from "../../globalVars/global.js";
import { ctx } from "../../globalVars/canvas.js";
import player from "../player/player.js";
import Buildable from "./buildable.js";
import RES from "../../resources.js";
import { buildingMenu } from "./buildingMenu.js";
import CVAR from "../../globalVars/const.js";
import socketClient from "../../init.js";
import Calc from "../../calc.js";
import camera from "../controller/camera.js";

export default class Building extends Buildable{
    constructor(x, y, type)
    {
        super(x, y, type);
        this._nowWorkIndex = 0
        this._craftingItems = new Array()
        this._level = 1;
        this._freeze = false
        this._slotsAmount = RES.buildings[type].maxSlots;
    }
    incSlotsAmount(){
        this._slotsAmount += 1
        socketClient.send(`buyslot/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
    }
    activateBooster(){
        if (this._craftingItems.length == 0){
            return
        }
        let timeCounter = 0;
        if (this._craftingItems[0].timeToFinish > (player._workBooster.boosterAmount-1)*player._workBooster.timeToEnd){
            this._craftingItems[0].workingTimeStamp = Date.now() + this._craftingItems[0].timeToFinish - (player._workBooster.boosterAmount - 1) * player._workBooster.timeToEnd + 1000
            return
        } else {
            this._craftingItems[0].workingTimeStamp = Date.now() + this._craftingItems[0].timeToFinish/player._workBooster.boosterAmount + 1000
            timeCounter += this._craftingItems[0].timeToFinish/player._workBooster.boosterAmount + 1000
        }

        let i;
        for (i = 1; i < this._craftingItems.length; i++) {
            if (this._craftingItems[i].timeToFinish > (player._workBooster.boosterAmount-1)*(player._workBooster.timeToEnd - timeCounter)){
                this._craftingItems[i].workingTimeStamp = this._craftingItems[i-1].workingTimeStamp + this._craftingItems[i].timeToFinish - (player._workBooster.boosterAmount - 1) * (player._workBooster.timeToEnd - timeCounter) + 1000
                break
            } else {
                this._craftingItems[i].workingTimeStamp = this._craftingItems[i-1].workingTimeStamp + this._craftingItems[i].timeToFinish/player._workBooster.boosterAmount + 1000
                timeCounter += this._craftingItems[i].timeToFinish/player._workBooster.boosterAmount + 1000 //перестраховка для бека
            }
        }
        for (let j = i+1; j < this._craftingItems.length; j++) {
            this._craftingItems[j].workingTimeStamp = this._craftingItems[j-1].workingTimeStamp + this._craftingItems[j].timeToFinish
        }
    }
    canUpgrade(){
        return player._money >= RES.buildings[this._type].upgradesPrice[this._level-1] && this._level < RES.buildings[this._type].maxLevel
    }
    upgrade(){
        player.buy(RES.buildings[this._type].upgradesPrice[this._level-1])
        this._level += 1
        socketClient.send(`upgrade/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
    }
    addSlot(slot){
        const item = {[slot.workName]: 1}
        item.workingTimeStamp = slot.workEndTimeStamp * 1000
        if (item.workingTimeStamp > Date.now()){
            let timeCounter = 0
            if (this._craftingItems.length > 0){
                timeCounter += this._craftingItems[this._craftingItems.length - 1].workingTimeStamp > Date.now() 
                ? this._craftingItems[this._craftingItems.length - 1].workingTimeStamp - Date.now()
                : 0
            }
            const maxTime = timeCounter < player._workBooster.timeToEnd
            ? player._workBooster.timeToEnd - timeCounter
            : 0

            const start = slot.workStartTimeStamp * 1000 > Date.now()
            ? slot.workStartTimeStamp * 1000
            : Date.now()

            const delta = item.workingTimeStamp - start

            const time = maxTime > delta 
            ? delta
            : maxTime
            
            item.timeToFinish = delta + (player._workBooster.boosterAmount-1)*time
        } else{
            item.timeToFinish = 0
            this._nowWorkIndex += 1
        }

        this._craftingItems.push(item)
    }
    canStartWork(item){
        return this._craftingItems.length < this._slotsAmount && player.canCraft(item) && item.minLevel <= this._level
    }
    startWork(item){
        this._freeze = true
        socketClient.send(`use/${Object.keys(item.products)[0]}/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
        const itemCopy = JSON.parse(JSON.stringify(item));
        player.craftItem(itemCopy)
        this._craftingItems.push(itemCopy.products);
        this._craftingItems[this._craftingItems.length-1].timeToFinish = itemCopy.timeToFinish * 1000
    }
    realStart(){
        if (player._workBooster.boosterAmount == 1){
            if (this._craftingItems.length > 1 && this._craftingItems[this._craftingItems.length-2].workingTimeStamp > Date.now()){
                this._craftingItems[this._craftingItems.length-1].workingTimeStamp = this._craftingItems[this._craftingItems.length-2].workingTimeStamp + this._craftingItems[this._craftingItems.length-1].timeToFinish;
            } else {
                this._craftingItems[this._craftingItems.length-1].workingTimeStamp = Date.now() + this._craftingItems[this._craftingItems.length-1].timeToFinish
            }
            return
        }

        if (this._craftingItems.length > 1 && this._craftingItems[this._craftingItems.length-2].workingTimeStamp > Date.now()){
            if (this._craftingItems[this._craftingItems.length-2].workingTimeStamp < player._workBooster.timeToEnd + Date.now()){
                if (this._craftingItems[this._craftingItems.length-1].timeToFinish > (player._workBooster.boosterAmount-1)*(player._workBooster.timeToEnd - (this._craftingItems[this._craftingItems.length-2].workingTimeStamp - Date.now()))){
                    this._craftingItems[this._craftingItems.length-1].workingTimeStamp = 
                    this._craftingItems[this._craftingItems.length-2].workingTimeStamp + 
                    this._craftingItems[this._craftingItems.length-1].timeToFinish - 
                    (player._workBooster.boosterAmount - 1) *
                    (player._workBooster.timeToEnd - (this._craftingItems[this._craftingItems.length-2].workingTimeStamp - Date.now()))
                } else{
                    this._craftingItems[this._craftingItems.length-1].workingTimeStamp = this._craftingItems[this._craftingItems.length-2].workingTimeStamp + this._craftingItems[this._craftingItems.length-1].timeToFinish/player._workBooster.boosterAmount
                }
            } else{
                this._craftingItems[this._craftingItems.length-1].workingTimeStamp = this._craftingItems[this._craftingItems.length-2].workingTimeStamp + this._craftingItems[this._craftingItems.length-1].timeToFinish    
            }
        } else {
            if (this._craftingItems[this._craftingItems.length-1].timeToFinish > (player._workBooster.boosterAmount-1)*player._workBooster.time){
                this._craftingItems[this._craftingItems.length-1].workingTimeStamp = Date.now() + this._craftingItems[this._craftingItems.length-1].timeToFinish - (player._workBooster.boosterAmount - 1) * player._workBooster.time
            } else{
                this._craftingItems[this._craftingItems.length-1].workingTimeStamp = Date.now() + this._craftingItems[this._craftingItems.length-1].timeToFinish/player._workBooster.boosterAmount
            }
        }
    }
    draw(){
        const out = (this._image.height - 16 * this._size.h)*CVAR.tileSide/16
        if (this._isMoving){
            ctx.shadowBlur = 5;
            ctx.shadowColor = this._canPut ? `rgb(0,${CVAR.greenColor},0)` : `rgb(${CVAR.redColor},0,0)`
        }
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
        ctx.shadowBlur = 0;
        if (this._craftingItems.length != 0 && 
            this._craftingItems[0].workingTimeStamp - Date.now() <= 0 && 
            this._craftingItems[0].timeToFinish == 0)
        {
            let key = Object.keys(this._craftingItems[0])[0]
            ctx.drawImage(RES.items[key].image, this._x + RES.buildings[this._type].productx, this._y + RES.buildings[this._type].producty, CVAR.itemMapSize, CVAR.itemMapSize)
        }
    }   
    update()
    {
        if (!this._freeze && this._nowWorkIndex < this._craftingItems.length){
            this._craftingItems[this._nowWorkIndex].timeToFinish = (this._craftingItems[this._nowWorkIndex].timeToFinish > 0 
            ? 
            (this._craftingItems[this._nowWorkIndex].timeToFinish - 1000)
            : 0);
            if (this._craftingItems[this._nowWorkIndex].workingTimeStamp - Date.now() <= 0)
            {
                this._craftingItems[this._nowWorkIndex].timeToFinish = 0
                this._nowWorkIndex += 1
                if (player._networth == 0){
                    const customEvent = new Event('firstBreadWait');
                    document.body.dispatchEvent(customEvent);
                }
            }
        }
    }
    collect()
    {
        if (this._craftingItems.length>0 && 
            this._craftingItems[0].workingTimeStamp - Date.now() <= 0 && 
            this._craftingItems[0].timeToFinish == 0)
        {
            const key = Object.keys(this._craftingItems[0])[0];
            if (player.getInvFullness()>=this._craftingItems[0][key]){
                GVAR.showFloatingItem(1, key, Calc.worldToScreen(this._x + this._w / 2, this._y + this._h / 2, camera.getPos(), GVAR.scale))
                player.pushInventory(key,this._craftingItems[0][key])
                this._craftingItems.shift()
                this._nowWorkIndex -= 1
                if (player._networth == 0){
                    const customEvent = new Event('firstBreadDone');
                    document.body.dispatchEvent(customEvent);
                }
            } else {
                GVAR.showFloatingText(3)    
                return false
            }
            socketClient.send(`collect/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
            return true
        }
        else {
            return false
        }
    }
    onClick() {
        if (!this.collect())
            buildingMenu.show(this)
    }
}