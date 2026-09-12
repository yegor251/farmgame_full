import { ctx } from "../../globalVars/canvas.js";
import CVAR from "../../globalVars/const.js";
import Calc from "../../calc.js";
import tiles from "../../globalVars/tiles.js";
import player from "../player/player.js";
import Sprite from "../sprite/sprite.js";
import RES from "../../resources.js";
import GVAR from "../../globalVars/global.js";
import camera from "../controller/camera.js";

export default class Plant extends Sprite{
    constructor(x, y, w, h, plantType)
    {
        super(x, y, w, h);
        this._image = RES.plants[plantType].image.stages[0]
        this._type = plantType;
        this._plantTimeStamp = RES.plants[plantType].seed.timeToGrow * 1000;
        this._timeToGrow = this._plantTimeStamp;
        this._grown = false;
    }
    draw(){
        const out = (this._image.height - 16 * this._h/CVAR.tileSide)*CVAR.tileSide/16 //смещение вверх из-за размера картинки
        ctx.drawImage(this._image, this._x, this._y - out, this._w, this._h + out);
    }
    updateGrowTime()
    {
        this._image = RES.plants[this._type].image.stages[Math.trunc(3-this._timeToGrow*3/this._plantTimeStamp)]
        this._timeToGrow = (this._timeToGrow != 0 ? (this._timeToGrow - 1000) : 0);
        if (this._growTimeStamp - Date.now() <= 0)
        {
            this._timeToGrow = 0
            this._grown = true;
        }
    }
    collect()
    {
        if (this._grown)
        {
            player.pushInventory(this._type, RES.plants[this._type].seed.amount);
            GVAR.showFloatingItem(RES.plants[this._type].seed.amount, this._type, Calc.worldToScreen(this._x + CVAR.tileSide / 2, this._y + CVAR.tileSide / 2, camera.getPos(), GVAR.scale))
            tiles[player._chosenTile.i][player._chosenTile.j]._structure._plant = 'none';
        }
    }
    move(pos) {
        this._x = pos.x;
        this._y = pos.y;
    }
}