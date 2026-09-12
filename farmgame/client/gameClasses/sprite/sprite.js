import { ctx } from "../../globalVars/canvas.js";
import camera from "../controller/camera.js";
import Calc from "../../calc.js";
import GVAR from "../../globalVars/global.js";

export default class Sprite{
    constructor(x, y, w, h, image)
    {
        this._x = x;
        this._y = y;
        this._w = w;
        this._h = h;
        this._image = image;
        this._rect = this.getRect();
        this._color = 'grey';
        this._hovered = false;
    }
    getRect(){
        return {
            x: this._x,
            y: this._y,
            w: this._w,
            h: this._h
        }
    }
    draw(){
        ctx.drawImage(this._image, this._rect.x, this._rect.y, this._rect.w, this._rect.h);
    }
    checkRectHover(mousePos){
        const worldMousePos = Calc.screenToWorld(mousePos.x, mousePos.y, camera.getPos(), GVAR.scale);
        this._hovered = Calc.pointInBoudaries(worldMousePos.x, worldMousePos.y, this.getRect());
    }
}