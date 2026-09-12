import Plant from "../plant/plant.js";
import RES from "../../resources.js";
import { ctx } from "../../globalVars/canvas.js";
import Buildable from "../building/buildable.js";
import { fieldMenu } from "./fieldMenu.js";
import player from "../player/player.js";
import socketClient from "../../init.js";
import CVAR from "../../globalVars/const.js";
import GVAR from "../../globalVars/global.js";

export default class Field extends Buildable{
    constructor(x, y, type)
    {
        super(x, y, type);
        this._image = RES.buildings[type].image
        this._plant = "none";
        this._freeze = false
    }
    activateBooster(){
        if (this._plant!='none' && this._plant._growTimeStamp > Date.now()){
            if (this._plant._timeToGrow > (player._growBooster.boosterAmount-1)*player._growBooster.timeToEnd){
                this._plant._growTimeStamp = Date.now() + this._plant._timeToGrow - (player._growBooster.boosterAmount - 1) * player._growBooster.timeToEnd + 1000 //перестраховка для бека
            } else {
                this._plant._growTimeStamp = Date.now() + this._plant._timeToGrow/player._growBooster.boosterAmount + 1000 //перестраховка для бека
            }
        }
    }
    draw(){
        if (this._isMoving){
            ctx.shadowBlur = 5;
            ctx.shadowColor = this._canPut ? `rgb(0,${CVAR.greenColor},0)` : `rgb(${CVAR.redColor},0,0)`
        }
        ctx.drawImage(this._image, this._x, this._y, this._w, this._h);
        ctx.shadowBlur = 0;
        if (this._plant!="none") this._plant.draw()
    }
    onClick()
    {
        if (this._plant._grown)
        {
            if (player.getInvFullness() >= RES.plants[this._plant._type].seed.amount){
                this.collect();
            } else{
                GVAR.showFloatingText(3)
            }
        } else {
            fieldMenu.show(this)
        }
    }
    collect(){
        this._plant.collect();
        socketClient.send(`collect/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
    }
    addSlot(slot){
        this._plant = new Plant(this._x, this._y, this._w, this._h, slot.workName)
        this._plant._growTimeStamp = slot.workEndTimeStamp * 1000
        if (Date.now() < this._plant._growTimeStamp){
            const time = this._plant._growTimeStamp - Date.now() < player._growBooster.timeToEnd 
            ? this._plant._growTimeStamp - Date.now() 
            : player._growBooster.timeToEnd
            this._plant._timeToGrow = this._plant._growTimeStamp - Date.now() + (player._growBooster.boosterAmount-1)*time
        } else {
            this._plant._timeToGrow = 0
        }
    }
    canCreatePlant(plant){
        return player._inventory[plant] > 0 && this._plant == "none"
    }
    createPlant(type)
    {
        this._plant = new Plant(this._x, this._y, this._w, this._h, type)
        this._freeze = true
        socketClient.send(`use/${type}/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
    }
    realStart(){
        if (player._growBooster.boosterAmount==1){
            this._plant._growTimeStamp = Date.now() + this._plant._plantTimeStamp
            return
        }
        if (this._plant._timeToGrow > (player._growBooster.boosterAmount-1)*player._growBooster.timeToEnd){
            this._plant._growTimeStamp = Date.now() + this._plant._timeToGrow - (player._growBooster.boosterAmount - 1) * player._growBooster.timeToEnd
        } else {
            this._plant._growTimeStamp = Date.now() + this._plant._timeToGrow/player._growBooster.boosterAmount
        }
    }
    move(pos) {
        this._floatX = pos.x;
        this._floatY = pos.y;
        this._x = Math.ceil(this._floatX/CVAR.tileSide)*CVAR.tileSide
        this._y = Math.ceil(this._floatY/CVAR.tileSide)*CVAR.tileSide
        pos.x = this._x
        pos.y = this._y
        if (this._plant != "none"){
            this._plant.move(pos);
        }
        GVAR.updateBuildingArr(this)
    }
    update(){
        if (!this._freeze && this._plant!="none"){
            this._plant.updateGrowTime()
        }
    }
}