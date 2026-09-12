import GVAR from "../../globalVars/global.js";
import player from "../player/player.js";
import socketClient from "../../init.js";
import Calc from "../../calc.js";
import CVAR from "../../globalVars/const.js";

class Spin {
    constructor() {
        document.getElementById('spin-button').onclick = () => {
            if (!player._isSpinActivated || (player._spinTimeStamp + CVAR.spinTime - Math.trunc(Date.now() / 1000)) < 0){
                if (player.getInvFullness() >= player._spinItems[player._spinDropIndex].amount || player._spinItems[player._spinDropIndex].item == 'money'){
                    player._isSpinActivated = true
                    player._spinTimeStamp = Math.trunc(Date.now() / 1000)
                    this.doSpin()
                    socketClient.send('spin')
                    socketClient.send('regen')
                    setTimeout(() => {  
                        GVAR.showFloatingItem(player._spinItems[player._spinDropIndex].amount, player._spinItems[player._spinDropIndex].item, {x: window.innerWidth / 2, y: window.innerHeight / 2})
                        this.renderSpin();
                    }, 4100);
                } else{
                    GVAR.showFloatingText(3)
                }
            }
        }
        document.getElementById("closeSpin").onclick = () => {
            this.close()
        }
        document.getElementById("spin-wrap").onclick = (e) => {
            if (e.target == document.getElementById("spin-wrap"))
                this.close()
        };
    }
    start(){
        setInterval(() => {
            if ((player._spinTimeStamp + CVAR.spinTime < Math.trunc(Date.now() / 1000))){
                socketClient.send('regen')
                player._spinTimeStamp = Math.trunc(Date.now() / 1000)
            } else {
                document.getElementById('spin-button').style.display = 'none'
                if (player._isSpinActivated) {
                    document.getElementById('spin-timer').style.display = 'flex'
                    document.getElementById('spin-timer').innerText = Calc.formatTime(player._spinTimeStamp + CVAR.spinTime - Math.trunc(Date.now() / 1000))
                } else {
                    document.getElementById('spin-wheel').style.transform = `rotate(0deg)`;
                    this.renderSpin()
                    document.getElementById('spin-timer').style.display = 'none'
                    document.getElementById('spin-button').style.display = 'flex'
                }
            }
        }, 1000);
    }
    show(){
        if ((player._spinTimeStamp + CVAR.spinTime - Math.trunc(Date.now() / 1000)) >= 0 && player._isSpinActivated){
            document.getElementById('spin-button').style.display = 'none'
        } else {
            document.getElementById('spin-timer').style.display = 'none'
            this.renderSpin();
        }
        GVAR.closeAllWindows()
        document.getElementById("spin-wrap").style.display = "flex";
    }
    close(){
        document.getElementById("spin-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
        document.getElementById('spin-wheel').style.transform = `rotate(0deg)`;
    }
    doSpin(){
        const container = document.getElementById('spin-wheel');
        let number = Math.ceil(360 - (Math.random()*180/player._spinItems.length + player._spinDropIndex*360/player._spinItems.length) + 720);
        container.style.transform = `rotate(${number}deg)`;
        document.getElementById('spin-button').style.display = 'none'
    }
    renderSpin(){
        const spin = document.getElementById('spin-wheel');
        spin.innerHTML = ""
        const size = player._spinItems.length
        for (let index = 0; index < size; index++) {
            const elem = document.createElement("div")
            elem.className = 'spin-elem'
            elem.style.transform = `rotate(${(index) * 360 / size}deg)`;

            const img = document.createElement("div")
            img.style.backgroundImage = `url(client/assets/items/${player._spinItems[index].item}.png)`
            img.className = "spin-image"
            const amount = document.createElement("h3")
            amount.className = "spin-text"
            amount.innerText = player._spinItems[index].amount
            elem.appendChild(img)
            elem.appendChild(amount)
            spin.appendChild(elem)
        }
    }
}
export const spin = new Spin();