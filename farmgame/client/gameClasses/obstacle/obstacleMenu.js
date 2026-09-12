import player from "../player/player.js";
import GVAR from "../../globalVars/global.js";
import tiles from "../../globalVars/tiles.js";
import Calc from "../../calc.js";
import CVAR from "../../globalVars/const.js";

class ObstacleMenu {
    constructor() {
        document.getElementById("close-obstacle-menu").onclick = () => {
            this.close()
        };
        document.getElementById("obstacle-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("obstacle-menu-wrap"))
                this.close()
        };
        this.obstacle = 'none';
    }
    show(obstacle) {
        this.obstacle = obstacle;
        GVAR.closeAllWindows();
        const img = document.getElementById('obstacle-img')
        img.style.backgroundImage = `url(client/assets/obstacles/${obstacle._type}/${obstacle._type}0.png)`;
        img.style.aspectRatio = `${obstacle._image.width} / ${obstacle._image.height}`
        document.getElementById("obstacle-menu-wrap").style.display = "flex";
        this.renderMenu();
    }
    close(){
        this.obstacle = 'none'
        document.getElementById("obstacle-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
    renderMenu() {
        const obstacleDelete = document.getElementById('obstacle-button');
        const money = document.getElementById('obstacle-money')
        if (this.obstacle._deletePrice){
            money.innerText = this.obstacle._deletePrice
            if (this.obstacle._deletePrice > player._money)
                document.getElementById('obstacle-money-checkmark').style.filter = 'grayscale(100%)';
            else
                document.getElementById('obstacle-money-checkmark').style.filter = 'grayscale(0%)';
        } else {
            money.innerText = '0'
            document.getElementById('obstacle-money-checkmark').style.filter = 'grayscale(0%)';
        }
        const token = document.getElementById('obstacle-token')
        if (this.obstacle._deleteTokenPrice){
            token.innerText = (this.obstacle._deleteTokenPrice / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0]
            if (this.obstacle._deleteTokenPrice > player._tokenBalance)
                document.getElementById('obstacle-token-checkmark').style.filter = 'grayscale(100%)';
            else
                document.getElementById('obstacle-token-checkmark').style.filter = 'grayscale(0%)';
        } else {
            token.innerText = '0'
            document.getElementById('obstacle-token-checkmark').style.filter = 'grayscale(0%)';
        }
        obstacleDelete.onclick = () => {
            document.getElementById('selection-menu-wrap').style.display = 'flex'
            document.getElementById('selection-text').innerText = GVAR.localization[36][GVAR.language]
            document.getElementById('selection-yes').onclick = () => {
                if (this.obstacle._deletePrice && this.obstacle._deletePrice > player._money){
                    GVAR.showFloatingText(1)
                } else {
                    if (this.obstacle._deleteTokenPrice && this.obstacle._deleteTokenPrice > player._tokenBalance){
                        GVAR.showFloatingText(2)
                    } else {
                        const tileIndex = Calc.CanvasToIndex(this.obstacle._x, this.obstacle._y, CVAR.tileSide, CVAR.outlineWidth);
                        for (let i = tileIndex.i; i < this.obstacle._w / CVAR.tileSide + tileIndex.i; i++) {
                            for (let j = tileIndex.j; j < this.obstacle._h / CVAR.tileSide + tileIndex.j; j++) {
                                tiles[i][j]._structure = "none"
                            }
                        }
                        if (this.obstacle._deletePrice && this.obstacle._deleteTokenPrice){
                            player.buy(this.obstacle._deletePrice)
                            player.spendToken(this.obstacle._deleteTokenPrice)
                        } else if (this.obstacle._deleteTokenPrice){
                            player.spendToken(this.obstacle._deleteTokenPrice)
                        } else {
                            player.buy(this.obstacle._deletePrice)
                        }
                        this.obstacle.delete()
                        this.close()
                        GVAR.showFloatingText(7)
                    }
                }
                document.getElementById('selection-menu-wrap').style.display = 'none'
            }
        }
    }
}
export const obstacleMenu = new ObstacleMenu();
