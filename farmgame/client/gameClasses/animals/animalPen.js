import RES from "../../resources.js";
import { ctx } from "../../globalVars/canvas.js";
import Buildable from "../building/buildable.js";
import Animal from "./animal.js";
import player from "../player/player.js";
import { animalMenu } from "./animalMenu.js";
import socketClient from "../../init.js";
import CVAR from "../../globalVars/const.js";
import GVAR from "../../globalVars/global.js";
import camera from "../controller/camera.js";
import Calc from "../../calc.js";

export default class AnimalPen extends Buildable{
    constructor(x, y, type)
    {
        super(x, y, type);
        this._animals = [];
        this._isWork = false;
        this._image = RES.buildings[type].image
        this._frontImage = RES.buildings[type].frontImage
        this._timeStamp = RES.buildings[this._type].speed * 1000;
        this._level = 1;
        this._speed = RES.buildings[this._type].speed * 1000;
        this._freeze = false
        this._feedType = Object.keys(RES.buildings[type].intake)[0]
    }
    activateBooster(){
        if (this._timeToFinish){
            if (this._timeToFinish > (player._workBooster.boosterAmount-1)*player._workBooster.timeToEnd){
                this._finishTime = Date.now() + this._timeToFinish - (player._workBooster.boosterAmount - 1) * player._workBooster.timeToEnd + 1000 //перестраховка для бека
            } else {
                this._finishTime = Date.now() + this._timeToFinish/player._workBooster.boosterAmount + 1000 //перестраховка для бека
            }
        }
    }
    setTime(endTime){
        this._finishTime = endTime * 1000
        if (Date.now() < this._finishTime){
            const time = this._finishTime - Date.now() < player._workBooster.timeToEnd 
            ? this._finishTime - Date.now() 
            : player._workBooster.timeToEnd
            this._timeToFinish = this._finishTime - Date.now() + (player._workBooster.boosterAmount-1)*time
        } else {
            this._timeToFinish = 0
        }
        this._isWork = true;
    }
    setLevel(level){
        this._level = level
        this._timeStamp -= Math.floor(this._speed * (CVAR.animalPenCoef - 1) * (level - 1))
    }
    upgrade(){
        player.buy(RES.buildings[this._type].upgradesPrice[this._level-1])
        this._level += 1
        this._timeStamp -= Math.floor(this._speed * (CVAR.animalPenCoef - 1))
        socketClient.send(`upgrade/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
    }
    draw(){
        if (this._isMoving){
            ctx.shadowBlur = 5;
            ctx.shadowColor = this._canPut ? `rgb(0,${CVAR.greenColor},0)` : `rgb(${CVAR.redColor},0,0)`
        }
        const out = (this._image.height - 16 * this._size.h)*CVAR.tileSide/16
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
        ctx.shadowBlur = 0;
        this._animals.forEach(animal => {
            animal.draw();
        });
        const perc = 1 - this._frontImage.height / this._image.height
        ctx.drawImage(this._frontImage, this._x, this._y - out + (this._h + out) * perc, this._w, this._frontImage.height * CVAR.tileSide / 16);
    }
    canStartWork(){
        return !this._isWork && this._animals.length!=0 && player._inventory[this._feedType] >= this._animals.length
    }
    startWork(){
        this._freeze = true
        socketClient.send(`use/start/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
        player._inventory[this._feedType] -= this._animals.length;
        this._timeToFinish = this._timeStamp;
        this._isWork = true;
    }
    realStart(){
        if (player._workBooster.boosterAmount==1){
            this._finishTime = Date.now() + this._timeStamp;
            return
        }
        if (this._timeToFinish > (player._workBooster.boosterAmount-1)*player._workBooster.timeToEnd){
            this._finishTime = Date.now() + this._timeToFinish - (player._workBooster.boosterAmount - 1) * player._workBooster.timeToEnd
        } else {
            this._finishTime = Date.now() + this._timeToFinish/player._workBooster.boosterAmount
        }
    }
    canAddAnimal(animal){
        return (this._animals.length < RES.buildings[this._type].maxAnimalAmount && animal === RES.buildings[this._type].animal)
    }
    addAnimal(){
        this._animals.push(new Animal(this._x + this._w/2, this._y + this._h/2,RES.buildings[this._type].animal,{x: this._x, y: this._y, w: this._w, h: this._h}))
        if (animalMenu.animalPen!='none'){
            animalMenu.renderMenu()
        }
    }
    update(){
        if (!this._freeze && this._isWork){
            this._timeToFinish = (this._timeToFinish > 0 
            ? 
            (this._timeToFinish - 1000)
            : 0);
            if (this._finishTime - Date.now() <= 0){
                this._timeToFinish = 0
                this._isWork = false;
                animalMenu.close()
                this._animals.forEach(animal => {
                    animal.isBlock = true
                });
            }
        }
    }
    updateAnimal(){
        this._animals.forEach(animal => {
            animal.update();
        });
        this._animals.sort((a, b) => a._y - b._y);
    }
    collect(){
        if (player.getInvFullness() >= this._animals.length){
            this._animals.forEach(animal => {
                animal.isBlock = false
            });
            const product = Object.keys(RES.buildings[this._type].products)[0]
            player.pushInventory(product, this._animals.length);
            GVAR.showFloatingItem(this._animals.length, product, Calc.worldToScreen(this._x + this._w / 2, this._y + this._h / 2, camera.getPos(), GVAR.scale))
            this._timeToFinish = undefined;
            socketClient.send(`collect/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
        } else{
            GVAR.showFloatingText(3)
        }
    }
    onClick()
    {
        if (this._timeToFinish == 0 && this._finishTime - Date.now() <= 0){
            this.collect()
        } else {
            animalMenu.show(this)
        }
    }
    move(pos) {
        const prev = {
            x: this._x,
            y: this._y
        }
        this._floatX = pos.x;
        this._floatY = pos.y;
        this._x = Math.ceil(this._floatX/CVAR.tileSide)*CVAR.tileSide
        this._y = Math.ceil(this._floatY/CVAR.tileSide)*CVAR.tileSide
        this._animals.forEach(el => {
            const a = {x: this._x - prev.x, y: this._y - prev.y}
            el.moveDelta(a)
        });
        GVAR.updateBuildingArr(this)
    }
}