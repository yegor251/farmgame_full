import GVAR from "../../globalVars/global.js";
import player from "../player/player.js";
import { pm } from "../ton-connect/tonMenu.js";
import { withdraw } from "../ton-connect/tonMenu.js";

class MainManu {
    constructor() {
        document.getElementById('open-main-menu').onclick = () => {
            this.show();
        }
        
        document.getElementById("close-main-menu").onclick = () => {
            this.close();
        }
        document.getElementById("networth-question-button").onclick = () => {
            GVAR.showFloatingText(15);
        }
        document.querySelectorAll('.donate-plus-button').forEach(button => {
            button.onclick = () => {
                pm.show();
                document.getElementById('main-menu-wrap').style.display = 'none';
            }
        });
        document.getElementById("token-withdraw-button").onclick = () => {
            withdraw.show();
        }
        this.link = `t.me/tonfarmgame_bot?start=${GVAR.tg_id}`
        document.getElementById("referral-link").innerText = `t.me/tonfarmgame_bot?start=${GVAR.tg_id}`
        document.getElementById('referral-text').innerText = GVAR.localization[49][GVAR.language]
        document.getElementById('referral-button-text').innerText = GVAR.localization[50][GVAR.language]
        document.querySelectorAll('.tap-to-copy').forEach(text => {
            text.innerText = GVAR.localization[17][GVAR.language];
        });
        document.getElementById("referral-yes").onclick = () => {
            GVAR.showFloatingText(22);
            document.getElementById("referral-menu-wrap").style.display = 'none'
            navigator.clipboard.writeText(this.link).then(() => {
            }).catch(err => {
                console.error("Failed to copy text: ", err);
            });
        }

        document.getElementById("referral-no").onclick = () => {
            document.getElementById("referral-menu-wrap").style.display = 'none'
        }

        document.getElementById("referral-container").onclick = () => {
            document.getElementById("referral-menu-wrap").style.display = 'flex'
        }
        document.getElementById("main-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("main-menu-wrap"))
                this.close()
        };
        document.getElementById("referral-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("referral-menu-wrap"))
                document.getElementById("referral-menu-wrap").style.display = 'none'
        };
    }
    show(){
        GVAR.closeAllWindows()
        this.renderMenu();
        document.getElementById("main-menu-wrap").style.display = "flex";
    }
    close(){
        document.getElementById("main-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
    renderMenu(){
        document.getElementById('farm-name').innerText = `${GVAR.tg_name}'s farm`;
        document.getElementById('money-balance').innerText = player._money;
        document.getElementById('networth-balance').innerText = player._networth;
        document.getElementById('token-balance').innerText = (player._tokenBalance / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0];
        document.getElementById('ton-balance').innerText = (player._tonBalance / 1000000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        document.getElementById('usdt-balance').innerText = (player._usdtBalance / 1000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        document.getElementById('main-menu-transactions').innerText = GVAR.localization[63][GVAR.language];
        document.getElementById('main-menu-boosters').innerText = GVAR.localization[65][GVAR.language];
        document.getElementById('main-menu-deals').innerText = GVAR.localization[66][GVAR.language];
    }
}
export const mainMenu = new MainManu();