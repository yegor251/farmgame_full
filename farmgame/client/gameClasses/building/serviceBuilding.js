import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import Sprite from "../sprite/sprite.js";
import RES from "../../resources.js";
import shop from "../shop/shop.js";
import { spin } from "../spin/spin.js";
import { orderManager } from "../orders/orders.js";
import GVAR from "../../globalVars/global.js";

export default class ServiceBuilding extends Sprite{
    constructor(x, y, type)
    {
        super(x, y);
        this._image = RES.buildings[type].image;
        this._type = type;
        this._w = RES.buildings[type].size.w * CVAR.tileSide;
        this._h = RES.buildings[type].size.h * CVAR.tileSide;
    }
    draw(){
        const out = (this._image.height - 16 * this._h/CVAR.tileSide)*CVAR.tileSide/16 //смещение вверх из-за размера картинки
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
    }
    onClick() {
        GVAR.closeAllWindows();
        if (this._type == 'barn')
            shop.drawStash()
        else if (this._type == 'spin_wheel')
            spin.show()
        else if (this._type == 'orders_board')
            orderManager.show()
    }
    update(){
    }
}