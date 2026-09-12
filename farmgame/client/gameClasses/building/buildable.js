import Sprite from "../sprite/sprite.js";
import RES from "../../resources.js";
import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import GVAR from "../../globalVars/global.js";

export default class Buildable extends Sprite{
    constructor(x, y, type)
    {
        super(x, y);
        this._floatX = this._x;
        this._floatY = this._y;
        this._type = type
        this._image = RES.buildings[type].image
        this._isMoving = false;
        this._canPut = true;
        this._prevPosition = {
            i: 0,
            j: 0
        }
        this._size = RES.buildings[type].size;
        this._w = this._size.w * CVAR.tileSide;
        this._h = this._size.h * CVAR.tileSide;
    }
    move(pos) {
        this._floatX = pos.x;
        this._floatY = pos.y;
        this._x = Math.ceil(this._floatX/CVAR.tileSide)*CVAR.tileSide
        this._y = Math.ceil(this._floatY/CVAR.tileSide)*CVAR.tileSide
        GVAR.updateBuildingArr(this)
    }
}