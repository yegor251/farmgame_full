import Sprite from "../sprite/sprite.js";
import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import RES from "../../resources.js";

export default class Phantom extends Sprite{
    constructor(x, y, size, type, image)
    {
        super(x, y);
        this._floatX = this._x;
        this._floatY = this._y;
        this._type = type
        this._image = image
        this._size = size
        this._isMoving = false
        this._canPut = true;
        this._w = this._size.w * CVAR.tileSide;
        this._h = this._size.h * CVAR.tileSide;
    }
    move(pos) {
        this._floatX = pos.x;
        this._floatY = pos.y;
        this._x = Math.ceil(this._floatX/CVAR.tileSide)*CVAR.tileSide
        this._y = Math.ceil(this._floatY/CVAR.tileSide)*CVAR.tileSide
    }
    draw () {
        let out = (this._image.height - 16 * this._size.h)*CVAR.tileSide/16
        ctx.shadowBlur = 5;
        ctx.shadowColor = this._canPut ? `rgb(0,${CVAR.greenColor},0)` : `rgb(${CVAR.redColor},0,0)`
        if (RES.names.animals.includes(this._type)){
            if (this._size.w < 1){
                out *= -1
                const outX = (this._image.width - 16 * this._size.w)*CVAR.tileSide/32
                ctx.drawImage(this._image, this._x + outX, this._y - out / 2, this._w, this._h);
            } else {
                ctx.drawImage(this._image, this._x, this._y, this._w, this._h);
            }
        } else
            ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
        ctx.shadowBlur = 0;
    }
}