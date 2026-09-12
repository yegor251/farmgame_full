import GVAR from "../../globalVars/global.js";
import Sprite from "../sprite/sprite.js";
import tiles from "../../globalVars/tiles.js";
import Calc from "../../calc.js";
import CVAR from "../../globalVars/const.js";
import Building from "../building/building.js";
import Field from "../field/field.js";
import RES from "../../resources.js";
import AnimalPen from "../animals/animalPen.js";
import Bush from "../bush/bush.js";
import ServiceBuilding from "../building/serviceBuilding.js";
import Obstacle from "../obstacle/obstacle.js";
import socketClient from "../../init.js";

export default class Tile extends Sprite{
    constructor(x, y, w, h, image)
    {
        super(x, y, w, h, image);
        this._structure = "none";
    }
    use(type){
        if (RES.buildingNames.bakery.includes(this._structure._type)){
            this._structure._freeze = false
            this._structure.realStart()
        } else if (RES.buildingNames.garden.includes(this._structure._type)){
            this._structure._freeze = false
            this._structure.realStart()
        } else if (RES.buildingNames.animalPen.includes(this._structure._type)){
            if (type=='start'){
                this._structure._freeze = false
                this._structure.realStart()
            }
        } else if (RES.buildingNames.bush.includes(this._structure._type)){
            this._structure._freeze = false
            this._structure.realStart()
        }
    }
    isCanPut(elem){
        let size = RES.buildings[elem._type].size;
        let tileIndex = Calc.CanvasToIndex(this._x, this._y, CVAR.tileSide, CVAR.outlineWidth);

        if (tileIndex.i+size.w>CVAR.tileRows || tileIndex.j+size.h>CVAR.tileCols)
            return false;
        for (let i = tileIndex.i; i < tileIndex.i + size.w; i++) {
            for (let j = tileIndex.j; j < tileIndex.j + size.h; j++) {
                if ((tiles[i][j]._structure != "none") && (tiles[i][j]._structure != elem)) {
                    return false;
                }
            }
        }
        return true;
    }
    createBuilding(type)
    {
        if (RES.buildingNames.animalPen.includes(type)){
            this._structure = new AnimalPen(this._x, this._y, type)
            GVAR.penArr.push(this._structure);
        }
        else if (type=="garden"){
            this._structure = new Field(this._x, this._y, type)
        } else if (RES.buildingNames.bush.includes(type)){
            this._structure = new Bush(this._x, this._y, type)
        } else if (RES.buildingNames.bakery.includes(type)){
            this._structure = new Building(this._x, this._y, type)
        } else if (RES.buildingNames.serviceBuildings.includes(type)){
            this._structure = new ServiceBuilding(this._x, this._y, type)
        } else if (RES.names.obstacles.includes(type)){
            this._structure = new Obstacle(this._x, this._y, type)
            GVAR.obstacleArr.push(this._structure);
            let tileIndex = Calc.CanvasToIndex(this._x, this._y, CVAR.tileSide, CVAR.outlineWidth);
            for (let i = tileIndex.i; i < tileIndex.i + RES.obstacles[type].size.w; i++) {
                for (let j = tileIndex.j; j < tileIndex.j + RES.obstacles[type].size.h; j++) {
                    tiles[i][j]._structure = this._structure;
                }
            }
            GVAR.addBuilding(this._structure);
            return
        }
        let tileIndex = Calc.CanvasToIndex(this._x, this._y, CVAR.tileSide, CVAR.outlineWidth);
        for (let i = tileIndex.i; i < tileIndex.i + RES.buildings[type].size.w; i++) {
            for (let j = tileIndex.j; j < tileIndex.j + RES.buildings[type].size.h; j++) {
                tiles[i][j]._structure = this._structure;
            }
        }
        GVAR.addBuilding(this._structure);
    }
    moveStructure(newPos){
        let el = this._structure
        let size = RES.buildings[el._type].size;
        socketClient.send(`move/${this._structure._prevPosition.i}/${this._structure._prevPosition.j}/${newPos.i}/${newPos.j}`)

        for (let i = el._prevPosition.i; i < el._prevPosition.i + size.w; i++) {
            for (let j = el._prevPosition.j; j < el._prevPosition.j + size.h; j++) {
                tiles[i][j]._structure="none";
            }
        }

        for (let i = newPos.i; i < newPos.i + size.w; i++) {
            for (let j = newPos.j; j < newPos.j + size.h; j++) {
                tiles[i][j]._structure=el;
            }
        }
        let pos = Calc.indexToCanvas(newPos.i, newPos.j, CVAR.tileSide, CVAR.outlineWidth);
        el.move(pos)
    }
}