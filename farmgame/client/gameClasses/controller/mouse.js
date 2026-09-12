import Calc from "../../calc.js";
import tiles from "../../globalVars/tiles.js";
import camera from "./camera.js";
import GVAR from "../../globalVars/global.js";
import CVAR from "../../globalVars/const.js";
import player from "../player/player.js";
import socketClient from "../../init.js";
import RES from "../../resources.js";

class Mouse{
    constructor() {
        this._LMBdown = false;
        this._screenPos = {
            x: 0,
            y: 0
        }
        this._mapPos = {
            i: 0,
            j: 0
        }
        this._deltaMove = {
            x: 0,
            y: 0
        }
        this._offset = {
            i: 0,
            j: 0
        }
        this._scale = 0;
        this._deltaScale = 0;
        this._movedDist = 0;
        this._LMBhold;
        this._isDragging = false;
        this._isOnBorder = false;
        this._isBlockAfterShop = false;
    }
    onMouseMove(e){
        const mousePos = Calc.getTouchPos(canvas, e);
        const index = Calc.screenToIndex(mousePos, camera.getPos(), GVAR.scale, CVAR.tileSide, CVAR.outlineWidth);
        GVAR.redraw = true;
        this._deltaMove.x = mousePos.x - this._screenPos.x;
        this._deltaMove.y = mousePos.y - this._screenPos.y;
        this._movedDist += Math.sqrt((this._deltaMove.x) * (this._deltaMove.x) + (this._deltaMove.y) * (this._deltaMove.y))
        this._screenPos = mousePos;
        this._mapPos = index;
        if (this._LMBdown && !this._isDragging)
        {
            camera.move(this._deltaMove.x / 1.2, this._deltaMove.y / 1.2);
        }
        if (GVAR.phantomStructureArr.length != 0){
            let pos = Calc.indexToCanvas(this._mapPos.i - this._offset.i, this._mapPos.j - this._offset.j, CVAR.tileSide, CVAR.outlineWidth);
            if (
                mouse._screenPos.x >= window.innerWidth * 0.95 ||
                mouse._screenPos.x <= window.innerWidth * 0.1 ||
                mouse._screenPos.y >= window.innerHeight * 0.95 ||
                mouse._screenPos.y <= window.innerHeight * 0.1
            ){
                this._isOnBorder = true
                const cameraCenter = {
                    i: Math.floor((camera._cameraIndexBoundingBox.left + camera._cameraIndexBoundingBox.right) / 2),
                    j: Math.floor((camera._cameraIndexBoundingBox.top + camera._cameraIndexBoundingBox.bottom) / 2)
                };
                const vector = {
                    di: this._mapPos.i - cameraCenter.i,
                    dj: this._mapPos.j - cameraCenter.j
                };
                const length = Math.sqrt(vector.di ** 2 + vector.dj ** 2);
                if (length == 0)
                    return
                const unitVector = {
                    di: vector.di / length,
                    dj: vector.dj / length
                };
                this._dirX = unitVector.di
                this._dirY = unitVector.dj
            } else{
                this._isOnBorder = false;
            }
            GVAR.phantomStructureArr[0].move(pos)
            if (tiles[mouse._mapPos.i - mouse._offset.i] == undefined || tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j] == undefined){
                GVAR.phantomStructureArr[0]._canPut = false
                return
            }
            if (player._phantomStructure.structureType == 'animal'){
                if (RES.buildingNames.animalPen.includes(tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j]._structure._type)){
                    GVAR.phantomStructureArr[0]._canPut = tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j]._structure.canAddAnimal(GVAR.phantomStructureArr[0]._type)
                } else {
                    GVAR.phantomStructureArr[0]._canPut = false
                }
            } else {
                GVAR.phantomStructureArr[0]._canPut = tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j].isCanPut(GVAR.phantomStructureArr[0])
            }
        }
    }
    onMouseDown(e)
    {
        this._movedDist=0;
        this.onMouseMove(e);
        this._LMBdown = true;
        this._movedDist=0;

        this._LMBhold = setTimeout(() => {
            const mousePos = Calc.getTouchPos(canvas, e);
            this._deltaMove.x = mousePos.x - this._screenPos.x;
            this._deltaMove.y = mousePos.y - this._screenPos.y;
            if (Math.sqrt((this._deltaMove.x) * (this._deltaMove.x) + (this._deltaMove.y) * (this._deltaMove.y))<10){
                if (this._mapPos.i<0 || this._mapPos.j<0 || this._mapPos.j>=CVAR.tileRows || this._mapPos.i>=CVAR.tileCols){
                    return
                }
                let el = tiles[this._mapPos.i][this._mapPos.j]._structure
                const a = Calc.CanvasToIndex(el._x, el._y, CVAR.tileSide, CVAR.outlineWidth)
                this._offset.i = this._mapPos.i - a.i
                this._offset.j = this._mapPos.j - a.j
                if (el!="none" && el._isMoving != undefined){
                    el._isMoving=true;
                    GVAR.redraw = true;
                    this._isDragging = true;
                    el._prevPosition = Calc.CanvasToIndex(el._x, el._y, CVAR.tileSide, CVAR.outlineWidth);
                    GVAR.phantomStructureArr.push(el)
                }
            }   
        }, 200);
    }
    onMouseUp(e)
    {
        if (player._phantomStructure!="none"){
            if (player._phantomStructure.structure._x>=0 && player._phantomStructure.structure._y>=0 && player._phantomStructure.structure._x<CVAR.tileSide*CVAR.tileCols && player._phantomStructure.structure._y<CVAR.tileSide*CVAR.tileRows){
                if (player._money >= player._phantomStructure.cost){
                    if (player._phantomStructure.structureType == 'building'){
                        if (tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j].isCanPut(player._phantomStructure.structure)){
                            tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j].createBuilding(player._phantomStructure.structure._type)
                            socketClient.send(`place/${player._phantomStructure.structure._type}/${mouse._mapPos.i}/${mouse._mapPos.j}`)
                            player.buy(player._phantomStructure.cost)
                            if (RES.buildingNames.bakery.concat(RES.buildingNames.animalPen).includes(player._phantomStructure.structure._type)){
                                RES.buildings[player._phantomStructure.structure._type].price *= CVAR.nextBuildingPriceCoef
                            } else if (player._phantomStructure.structure._type == 'garden'){
                                RES.buildings['garden'].floatPrice *= CVAR.nextGardenPriceCoef
                                RES.buildings['garden'].price = Math.floor(RES.buildings['garden'].floatPrice)
                            }
                            if (player._phantomStructure.structure._type == 'garden' && GVAR.countBuilding('garden') == 1){
                                const customEvent = new Event('firstGardenPlace');
                                document.body.dispatchEvent(customEvent);
                            } else if (player._phantomStructure.structure._type == 'bakery' && GVAR.countBuilding('bakery') == 1){
                                const customEvent = new Event('firstBuildingPlace');
                                document.body.dispatchEvent(customEvent);
                            }
                            player._phantomStructure = "none"
                        } else {
                            GVAR.showFloatingText(10)
                            if (player._phantomStructure.structure._type == 'garden' && GVAR.countBuilding('garden') == 0){
                                const customEvent = new Event('firstGardenPlaceBad');
                                document.body.dispatchEvent(customEvent);
                            } else if (player._phantomStructure.structure._type == 'bakery' && GVAR.countBuilding('bakery') == 0) {
                                const customEvent = new Event('firstBuildingPlaceBad');
                                document.body.dispatchEvent(customEvent);
                            }
                        }
                    } else if (player._phantomStructure.structureType == 'animal' && RES.buildingNames.animalPen.includes(tiles[mouse._mapPos.i][mouse._mapPos.j]._structure._type) && tiles[mouse._mapPos.i][mouse._mapPos.j]._structure.canAddAnimal(player._phantomStructure.structure._type)){
                        tiles[mouse._mapPos.i][mouse._mapPos.j]._structure.addAnimal()
                        const x = tiles[mouse._mapPos.i][mouse._mapPos.j]._structure._x
                        const y = tiles[mouse._mapPos.i][mouse._mapPos.j]._structure._y
                        socketClient.send(`use/buy/${x/CVAR.tileSide}/${y/CVAR.tileSide}`)
                        player.buy(player._phantomStructure.cost)
                        player._phantomStructure = "none"
                    } else {
                        GVAR.showFloatingText(11)
                    }
                }
                this._isBlockAfterShop = false;
            } else {
                GVAR.showFloatingText(10)
            }
        }
        GVAR.phantomStructureArr.pop()
        player._phantomStructure = "none"

        GVAR.buildableArr.forEach((el) => {
            if (el._isMoving)
            {
                if (el._x>=0 && el._y>=0 && el._x<CVAR.tileSide*CVAR.tileCols && el._y<CVAR.tileSide*CVAR.tileRows && tiles[mouse._mapPos.i - mouse._offset.i][mouse._mapPos.j - mouse._offset.j].isCanPut(el)){
                    const pos = Calc.CanvasToIndex(el._x, el._y, CVAR.tileSide, CVAR.outlineWidth)
                    tiles[el._prevPosition.i][el._prevPosition.j].moveStructure(pos)
                }
                else {
                    GVAR.showFloatingText(10)
                    let prevPos = Calc.indexToCanvas(el._prevPosition.i, el._prevPosition.j, CVAR.tileSide, CVAR.outlineWidth);
                    el.move(prevPos)
                }
                el._isMoving=false;
                GVAR.phantomStructureArr.pop()
            }
        })

        this._LMBdown = false;
        clearTimeout(this._LMBhold);        
        const mousePos = Calc.getTouchEndPos(canvas, e);
        const index = Calc.screenToIndex(mousePos, camera.getPos(), GVAR.scale, CVAR.tileSide, CVAR.outlineWidth);
        GVAR.redraw = true;
        this._screenPos = mousePos;
        this._mapPos = index;
        this._isDragging = false;
        this._offset.i = 0
        this._offset.j = 0
        if (this._movedDist < 10)
        {
           this.onClick();
        }
        this._movedDist = 0;
        this._isOnBorder = false
    }
    moveBuildablePrevPos(){
        GVAR.buildableArr.forEach((el) => {
            if (el._isMoving)
            {
                let prevPos = Calc.indexToCanvas(el._prevPosition.i, el._prevPosition.j, CVAR.tileSide, CVAR.outlineWidth);
                el.move(prevPos)
                el._isMoving=false;
                GVAR.phantomStructureArr.pop()
            }
        })
        GVAR.redraw = true
        this._isOnBorder = false
    }
    onClick()
    {
        if (this._mapPos.i<0 || this._mapPos.j<0 || this._mapPos.j>=CVAR.tileRows || this._mapPos.i>=CVAR.tileCols)
            return
        player._chosenTile = {
            i: this._mapPos.i,
            j: this._mapPos.j,
        }
        if (tiles[player._chosenTile.i][player._chosenTile.j]._structure != "none"){
            player._lastStructure = tiles[player._chosenTile.i][player._chosenTile.j]._structure
            tiles[player._chosenTile.i][player._chosenTile.j]._structure.onClick();
        }
    }
    onScaleStart(e)
    {
        this._scale = Calc.getTouchesDistance(e) / 100;
    }
    onScale(e)
    {
        const newScale = Calc.getTouchesDistance(e) / 100;
        this._deltaScale = (newScale - this._scale) * 1.5;
        this._scale = newScale;
        let otn = (GVAR.scale + this._deltaScale) / GVAR.scale ;
        if ((GVAR.scale + this._deltaScale) >= CVAR.minScale && (GVAR.scale + this._deltaScale) <= CVAR.maxScale){
            GVAR.scale = GVAR.scale + this._deltaScale
            camera.updateMapBoundingBox()
        } else if ((GVAR.scale + this._deltaScale) < CVAR.minScale){
            if (GVAR.scale > CVAR.minScale){
                otn = CVAR.minScale / GVAR.scale
                GVAR.scale = CVAR.minScale
                camera.updateMapBoundingBox()
                GVAR.redraw = true;
            } else{
                return
            }
        } else {
            if (GVAR.scale < CVAR.maxScale){
                otn = CVAR.maxScale / GVAR.scale
                GVAR.scale = CVAR.maxScale
                camera.updateMapBoundingBox()
                GVAR.redraw = true;
            } else{
                return
            }
        }
        const approximationCenter = Calc.getApproximationCenter(e);
        let d = Math.sqrt((approximationCenter.x)*(approximationCenter.x) + (approximationCenter.y)*(approximationCenter.y))
        let s = d - d/(otn)
        const newX = (camera._x + s * (approximationCenter.x) / d)*otn
        const newY = (camera._y + s * (approximationCenter.y) / d)*otn
        camera.move(camera._x - newX, camera._y - newY)
        camera.updateBoundingBox();
        GVAR.redraw = true;
    }
}
const mouse = new Mouse();

export default mouse