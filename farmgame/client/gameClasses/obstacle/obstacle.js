import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import Sprite from "../sprite/sprite.js";
import RES from "../../resources.js";
import { obstacleMenu } from "./obstacleMenu.js";
import GVAR from "../../globalVars/global.js";
import socketClient from "../../init.js";

export default class Obstacle extends Sprite{
    constructor(x, y, type)
    {
        super(x, y);
        this._image = RES.obstacles[type].image[0];
        this._currImageInd = 0
        this._type = type;
        this._w = RES.obstacles[type].size.w * CVAR.tileSide;
        this._h = RES.obstacles[type].size.h * CVAR.tileSide;
        this._deletePrice = RES.obstacles[type].removePrice
        this._deleteTokenPrice = RES.obstacles[type].removeTokenPrice
        this._stagesCount = RES.obstacles[type].stages
    }
    draw(){
        const out = (this._image.height - 16 * this._h/CVAR.tileSide)*CVAR.tileSide/16 //смещение вверх из-за размера картинки
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
    }
    changeImage(){
        this._currImageInd = (this._currImageInd + 1) % this._stagesCount
        this._image = RES.obstacles[this._type].image[this._currImageInd];
    }
    onClick() {
        obstacleMenu.show(this)
    }
    delete(){
        socketClient.send(`rmobstacle/${this._x/CVAR.tileSide}/${this._y/CVAR.tileSide}`)
        GVAR.obstacleArr = GVAR.obstacleArr.filter(item => item !== this);
        GVAR.buildableArr = GVAR.buildableArr.filter(item => item !== this);
    }
}