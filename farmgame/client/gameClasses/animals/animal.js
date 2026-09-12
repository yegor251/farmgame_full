import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import Sprite from "../sprite/sprite.js";
import RES from "../../resources.js";

export default class Animal extends Sprite{
    constructor(x, y, type, range)
    {
        super(x, y);
        this.range = range
        this.standImages = RES.animals[type].standImages
        this.currStandInd = 0
        this.goImages = RES.animals[type].goImages
        this.currGoInd = 0
        this._image = this.goImages[0]
        this._h = RES.animals[type].size.h * CVAR.tileSide
        this._w = RES.animals[type].size.w * CVAR.tileSide
        this.range.w -= this._w
        this.range.h -= this._h
        this.range.y += RES.animals[type].badZone
        this.range.h -= RES.animals[type].badZone
        this.nextCoords = this._getRandomPoint(range)
        this.timer = 0
        this.stopTimeAmount = 100
        this.stopTime = 10
        this.direction = 1
        this.isChange = false
        this.isBlock = false
        this.finalImage = RES.animals[type].finalImage
    }
    draw(){
        if (this.isBlock){
            ctx.drawImage(this.finalImage, this._x, this._y, this._w, this._h);
        }else if (this.direction == 1){
            ctx.drawImage(this._image, this._x, this._y, this._w, this._h);
        }else {
            ctx.save();
            ctx.translate(this._x + this._w, this._y);
            ctx.scale(-1, 1);
            ctx.drawImage(this._image, 0, 0, this._w, this._h);
            ctx.restore();
        }
    }
    update() {
        if (this.isBlock)
            return
        if (this.timer == 0){
            if (this.isChange){
                this._image = this.goImages[this.currGoInd]
                this.currGoInd = (this.currGoInd + 1) % this.goImages.length
            }
            this.isChange = !this.isChange

            const deltaX = this.nextCoords.x - this._x;
            const deltaY = this.nextCoords.y - this._y;
            if (deltaX < 0 && this.direction == 1){
                this.direction = -1;
            } else if (deltaX >=0 && this.direction == -1){
                this.direction = 1;
            }

            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

            const stepX = (deltaX / (distance * 2)) || 0;
            const stepY = (deltaY / (distance * 2)) || 0;

            this._x += stepX;
            this._y += stepY;

            if (Math.abs(this._x - this.nextCoords.x) < 0.7 && Math.abs(this._y - this.nextCoords.y) < 0.7) {
                this.nextCoords = this._getRandomPoint(this.range)
                this.timer = 1
            }
        }
        else {
            if (this.timer == 1){
                this._image = this.standImages[this.currStandInd]
                this.currStandInd = (this.currStandInd + 1) % this.standImages.length
            }
            this.timer += 1;
            if (this.timer % 20 == 0){
                this._image = this.standImages[this.currStandInd]
                this.currStandInd = (this.currStandInd + 1) % this.standImages.length
            }
            if (this.timer==this.stopTime){
                this.timer = 0
                this.stopTime = 10 + Math.floor(Math.random() * this.stopTimeAmount)
            }
        }
    }
    moveDelta(delta){
        this._x += delta.x;
        this._y += delta.y;
        this.nextCoords.x += delta.x;
        this.nextCoords.y += delta.y;
        this.range.x += delta.x;
        this.range.y += delta.y;
    }
    _getRandomPoint(range) {
        const side = Math.floor(Math.random() * 4); // Случайно выбираем одну из 4 сторон
        let x, y;
        
        switch (side) {
            case 0: // Верхняя сторона
                x = range.x + Math.floor(Math.random() * range.w);
                y = range.y;
                break;
            case 1: // Правая сторона
                x = range.x + range.w;
                y = range.y + Math.floor(Math.random() * range.h);
                break;
            case 2: // Нижняя сторона
                x = range.x + Math.floor(Math.random() * range.w);
                y = range.y + range.h;
                break;
            case 3: // Левая сторона
                x = range.x;
                y = range.y + Math.floor(Math.random() * range.h);
                break;
        }
    
        return {x: x, y: y};
    }    
}