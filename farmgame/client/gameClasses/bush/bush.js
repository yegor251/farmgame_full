import RES from "../../resources.js";
import { ctx } from "../../globalVars/canvas.js";
import Buildable from "../building/buildable.js";
import player from "../player/player.js";
import { bushMenu } from "./bushMenu.js";
import socketClient from "../../init.js";
import CVAR from "../../globalVars/const.js";
import GVAR from "../../globalVars/global.js";
import camera from "../controller/camera.js";
import Calc from "../../calc.js";

export default class Bush extends Buildable{
    constructor(x, y, type)
    {
        super(x, y, type);
        this._image = RES.buildings[type].image[0]
        this._timeStamp = RES.buildings[this._type].speed * 1000;
        this._freeze = false;
        this._collectedAmountLimit = RES.buildings[this._type].productLimit;
        this._collectedAmount = 0;
        this._resetPrice = RES.buildings[this._type].price * 2
        this.startWork()
    }
    activateBooster(){
        if (this._timeToFinish){
            if (this._timeToFinish > (player._growBooster.boosterAmount-1)*player._growBooster.timeToEnd){
                this._finishTime = Date.now() + this._timeToFinish - (player._growBooster.boosterAmount - 1) * player._growBooster.timeToEnd + 1000 //перестраховка для бека
            } else {
                this._finishTime = Date.now() + this._timeToFinish/player._growBooster.boosterAmount + 1000 //перестраховка для бека
            }
        }
    }
    setProperties(endTime, intData){
        this._collectedAmount = intData
        if (intData < this._collectedAmountLimit){
            this._finishTime = endTime * 1000
            if (Date.now() < this._finishTime){
                const time = this._finishTime - Date.now() < player._growBooster.timeToEnd 
                ? this._finishTime - Date.now() 
                : player._growBooster.timeToEnd
                this._timeToFinish = this._finishTime - Date.now() + (player._growBooster.boosterAmount-1)*time
            } else {
                this._timeToFinish = 0
            }
            this._isWork = true;
            this._freeze = false
        } else{
            this._timeToFinish = undefined
            this._isWork = false;
            this._image = RES.buildings[this._type].image[2]
        }
    }
    draw(){
        if (this._isMoving){
            ctx.shadowBlur = 5;
            ctx.shadowColor = this._canPut ? `rgb(0,${CVAR.greenColor},0)` : `rgb(${CVAR.redColor},0,0)`
        }
        const out = (this._image.height - 16 * this._size.h)*CVAR.tileSide/16
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
        ctx.shadowBlur = 0;
    }
    canReset(){
        return this._collectedAmount >= this._collectedAmountLimit
    }
    reset(){
        socketClient.send(`use/null/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
        this._collectedAmount = 0;
        player.buy(this._resetPrice)
        this.startWork()
        this._image = RES.buildings[this._type].image[0]
    }
    canStartWork(){
        return (!this._isWork && this._collectedAmount < this._collectedAmountLimit)
    }
    startWork(){
        this._freeze = true
        this._timeToFinish = this._timeStamp;
        this._isWork = true;
    }
    realStart(){
        if (player._growBooster.boosterAmount==1){
            this._finishTime = Date.now() + this._timeStamp;
            return
        }
        if (this._timeToFinish > (player._growBooster.boosterAmount-1)*player._growBooster.timeToEnd){
            this._finishTime = Date.now() + this._timeToFinish - (player._growBooster.boosterAmount - 1) * player._growBooster.timeToEnd
        } else {
            this._finishTime = Date.now() + this._timeToFinish/player._growBooster.boosterAmount
        }
    }
    update(){
        if (!this._freeze && this._isWork && this._timeToFinish != undefined){
            this._timeToFinish = (this._timeToFinish != 0 
            ? 
            (this._timeToFinish - 1000)
            : 0);
            if (this._finishTime - Date.now() <= 0){
                this._timeToFinish = 0
                this._image = RES.buildings[this._type].image[1]
                this._isWork = false;
            }
        }
    }
    collect(){
        const key = Object.keys(RES.buildings[this._type].products)[0]
        const amount = RES.buildings[this._type].products[key]
        if (player.getInvFullness() >= amount){
            player.pushInventory(key, amount);
            GVAR.showFloatingItem(amount, key, Calc.worldToScreen(this._x + this._w / 2, this._y + this._h / 2, camera.getPos(), GVAR.scale))
            this._timeToFinish = undefined;
            socketClient.send(`collect/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
            this._collectedAmount += 1
            if (this._collectedAmount < this._collectedAmountLimit){
                this._isWork = true
                this._timeToFinish = this._timeStamp;
                this.realStart()
            }
        } else
            GVAR.showFloatingText(3)
        if (this._collectedAmount == this._collectedAmountLimit)
            this._image = RES.buildings[this._type].image[2]
        else
            this._image = RES.buildings[this._type].image[0]
    }
    onClick()
    {
        if (this._timeToFinish == 0 && this._finishTime - Date.now() <= 0){
            this.collect()
        } else {
            bushMenu.show(this)
        }
    }
}