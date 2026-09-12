import dealL from "../../assets/deals/deal_l.js";
import Calc from "../../calc.js";
import CVAR from "../../globalVars/const.js";
import GVAR from "../../globalVars/global.js";
import socketClient from "../../init.js";
import player from "../player/player.js";

const tonweb = new window.TonWeb();

class PayMenu {
    constructor() {
        this.walletDisconnected();

        this.tonConnectUI = new TON_CONNECT_UI.TonConnectUI({
            manifestUrl: 'https://www.jsonkeeper.com/b/TE7Z',
            buttonRootId: "ton-connect-button"
        });

        this.tonConnectUI.onStatusChange((wallet) => {
            if (wallet) {
                this.walletConnected();
            }
            else
            {
                this.walletDisconnected();
            }
        })

        document.getElementById('close-payments').onclick = () => {
            this.close()
        }
        document.getElementById("payment-wrap").onclick = (e) => {
            if (e.target == document.getElementById("payment-wrap"))
                this.close()
        };
        document.getElementById("adress-copy-div").addEventListener("click", function() {
            GVAR.showFloatingText(22);
            navigator.clipboard.writeText(CVAR.wallet).then(() => {
            }).catch(err => {
                console.error("Failed to copy text: ", err);
            });
        });
        document.getElementById("memo-copy-div").addEventListener("click", function() {
            GVAR.showFloatingText(22);
            navigator.clipboard.writeText(GVAR.tg_id).then(() => {
            }).catch(err => {
                console.error("Failed to copy text: ", err);
            });
        });
    }
    close(){
        document.getElementById("payment-wrap").style.display = 'none';
        document.getElementById("main-menu-wrap").style.display = "flex";
    }
    show() {
        document.getElementById("payment-wrap").style.display = "flex";
        document.getElementById("manual-pay-text").innerText = GVAR.localization[16][GVAR.language];
        document.getElementById("adress-text").innerText = CVAR.wallet;
        document.querySelectorAll('.tap-to-copy').forEach(text => {
            text.innerText = GVAR.localization[17][GVAR.language];
        });
        document.getElementById("memo-warning-text").innerText = GVAR.localization[18][GVAR.language];
        document.getElementById("memo-text").innerText = GVAR.tg_id;
        document.getElementById("or-text").innerText = GVAR.localization[19][GVAR.language];
        document.getElementById("payment-ton-text").innerText = GVAR.localization[20][GVAR.language];
        document.getElementById("deposit-text").innerText = GVAR.localization[21][GVAR.language];
    }
    walletConnected() {
        document.getElementById("ton-amount").style.display = "flex";
        document.getElementById("proceed-to-buy").style.display = "flex";
        document.getElementById("proceed-to-buy").onclick = async () => {
            const s = document.getElementById("ton-amount").value;
            if (!isNaN(parseFloat(s)) && isFinite(s) && parseFloat(s) > 0) {
                const amount = Math.trunc(parseFloat(s) * 1000000000);
                await this.purchaseTon(amount);
            } else {
                GVAR.showFloatingText(23);
            }
        }
    }
    walletDisconnected() {
        document.getElementById("ton-amount").style.display = "none";
        document.getElementById("proceed-to-buy").style.display = "none";
    }
    async generatePayload(amount) {
        let a = new tonweb.boc.Cell();
        a.bits.writeUint(0, 32);
        a.bits.writeString(`${amount}`);
        let payload = tonweb.utils.bytesToBase64(await a.toBoc());
        return payload
    }
    async purchaseTon(amount) {
        var payload = await this.generatePayload(GVAR.tg_id);

        const transaction = {
            validUntil: Math.floor(Date.now() / 1000) + 120, // 120 sec
            messages: [
                {
                    address: CVAR.wallet,
                    amount: `${amount}`,
                    payload: `${payload}`
                }
            ]
        }
        
        try {
            const result = await this.tonConnectUI.sendTransaction(transaction);
            const someTxData = await myAppExplorerService.getTransaction(result.boc);
            console.log('Transaction successful:', someTxData);
        } catch (e) {
            console.error('Transaction failed:', e);
        }
    }
}

export const pm = new PayMenu();

class DealsMenu
{
    constructor() {
        document.getElementById("open-deals").onclick = () => {
            GVAR.closeAllWindows();
            document.getElementById("deals-wrap").style.display = 'flex';
            this.show();
        }

        document.getElementById("close-deals").onclick = () => {
            this.close()
        }
        document.getElementById("deals-wrap").onclick = (e) => {
            if (e.target == document.getElementById("deals-wrap"))
                this.close()
        };
        document.getElementById("selection-deal-no").onclick = () => {
            document.getElementById("selection-deal-wrap").style.display = "none"
        }
        document.getElementById("selection-deal-text").innerText = GVAR.localization[62][GVAR.language]
        document.getElementById("selection-deal-wrap").onclick = (event) => {
            if (event.target === event.currentTarget) {
                document.getElementById("selection-deal-wrap").style.display = 'none'
            }
        }
    }
    close(){
        document.getElementById("deals-wrap").style.display = "none";
        document.getElementById("main-menu-wrap").style.display = "flex";
    }
    show() {
        document.getElementById('deal-ton-balance').innerText = (player._tonBalance / 1000000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        document.getElementById('deal-usdt-balance').innerText = (player._usdtBalance / 1000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        const dealsWrap = document.getElementById("deals-list");
        dealsWrap.innerHTML = ''
        if (Object.keys(player._availableDeals).length === 0){
            const text = document.createElement('h3');
            text.className = 'deal-empty-text'
            text.innerText = GVAR.localization[14][GVAR.language];
            dealsWrap.appendChild(text)
        }
        const menu = this
        for (const dealKey in player._availableDeals) {
            const deal = player._availableDeals[dealKey];
            
            const dealImg = document.createElement('div')
            dealImg.className = 'deal'
            dealImg.style.backgroundImage = `url(client/assets/deals/${dealKey}.png)`

            const priceCont = document.createElement('div')
            priceCont.className = 'deal-price-cont'
            const price = document.createElement('h3')
            price.className = 'deal-price'
            const priceImg = document.createElement('div')
            priceImg.className = 'deal-price-img'
            if (deal.usdtPrice) {
                price.innerText = (deal.usdtPrice / 1000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0]
                priceImg.style.backgroundImage = `url(client/assets/design/usdt.png)`
            } else if (deal.tonPrice) {
                price.innerText = (deal.tonPrice / 1000000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0]
                priceImg.style.backgroundImage = `url(client/assets/design/ton.png)`
            }
            priceCont.appendChild(price)
            priceCont.appendChild(priceImg)
            dealImg.appendChild(priceCont)

            const nameCont = document.createElement('div')
            nameCont.className = 'deal-name-cont'
            const name = document.createElement('h3')
            name.className = 'deal-name'
            name.innerText = dealL.localization[dealKey][GVAR.language]
            nameCont.appendChild(name)
            dealImg.appendChild(nameCont)

            const dealCont = document.createElement('div')
            dealCont.className = 'deal-content'
            dealImg.appendChild(dealCont)
            if (deal.reward.token) {
                const dealItem = document.createElement('div')
                dealItem.className = 'deal-item'

                const dealShadow = document.createElement('div')
                dealShadow.className = 'deal-item-shadow'
                dealItem.appendChild(dealShadow)

                const dealItemImg = document.createElement('div')
                dealItemImg.className = 'deal-item-img'
                dealItemImg.style.backgroundImage = `url(client/assets/design/token.png)`
                dealItem.appendChild(dealItemImg)

                const dealItemT2 = document.createElement('h3')
                dealItemT2.className = 'deal-item-text2'
                dealItemT2.innerText = (deal.reward.token / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0]
                dealItem.appendChild(dealItemT2)

                dealCont.appendChild(dealItem)
            }
            deal.reward.boosters.forEach(booster => {
                const dealItem = document.createElement('div')
                dealItem.className = 'deal-item'

                const dealShadow = document.createElement('div')
                dealShadow.className = 'deal-item-shadow'
                dealItem.appendChild(dealShadow)

                const dealItemImg = document.createElement('div')
                dealItemImg.className = 'deal-item-img'
                dealItemImg.style.backgroundImage = `url(client/assets/design/${booster.boosterType}.png)`
                dealItem.appendChild(dealItemImg)

                const dealItemT1 = document.createElement('h3')
                dealItemT1.className = 'deal-item-text1'
                dealItemT1.innerText = Calc.formatTime(booster.time)
                dealItem.appendChild(dealItemT1)

                const dealItemT2 = document.createElement('h3')
                dealItemT2.className = 'deal-item-text2'
                dealItemT2.innerText = 'x'
                if (booster.boosterType == "GrowSpeed" || booster.boosterType == "WorkSpeed"){
                    dealItemT2.innerText += 100 / (100 - booster.percentage)
                } else if (booster.boosterType == "OrderMoney"){
                    dealItemT2.innerText += booster.percentage / 100 + 1
                } else if (booster.boosterType == "OrderItems"){
                    dealItemT2.innerText += booster.percentage / 100
                }
                dealItem.appendChild(dealItemT2)


                dealCont.appendChild(dealItem)
            });

            dealImg.onclick = () => {
                document.getElementById("selection-deal-wrap").style.display = "flex"
                document.getElementById("selection-deal-yes").onclick = () => {
                    const canBuy = (deal.tonPrice && player._tonBalance >= deal.tonPrice) ||
                     (deal.usdtPrice && player._usdtBalance >= deal.usdtPrice);
                    if (canBuy){
                        socketClient.send(`buydeal/${dealKey}`)
                        socketClient.send(`regen`)
                        if (deal.tonPrice)
                            player._tonBalance -= deal.tonPrice
                        else {
                            player._usdtBalance -= deal.usdtPrice
                        }
                        delete player._availableDeals[dealKey];
                        GVAR.showFloatingText(7)
                        menu.show()
                    } else {
                        GVAR.showFloatingText(2)
                    }
                    document.getElementById("selection-deal-wrap").style.display = "none"
                }
            }
            dealsWrap.appendChild(dealImg);
        }
    }
}

export const dealmenu = new DealsMenu();

class WithdrawMenu
{
    constructor() {
        document.getElementById("close-withdraw-menu").onclick = () => {
            this.close()
        }
        document.getElementById("withdraw-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("withdraw-menu-wrap"))
                this.close()
        };

        function isValidTonAddress(address) {
            try {
                const decodedAddress = new tonweb.utils.Address(address);
                return true;
            } catch (error) {
                return false;
            }
        }

        document.getElementById('confirm-withdraw').onclick = () => {
            const wallet = document.getElementById('withdraw-adress').value
            if (isValidTonAddress(wallet)){
                let flag = true
                let amount = 0;
                try {
                    amount = Math.round(parseFloat(document.getElementById('withdraw-amount').value)*100)
                    if (amount <=0){
                        flag = false
                    }
                } catch (error) {
                    flag = false
                }
                if (flag && amount) {
                    if (amount > 0 && amount <= player._tokenBalance){
                        if (player._tonBalance >= CVAR.transactionFee){
                            socketClient.send(`withdraw/${amount}/${wallet}`)
                            GVAR.showFloatingText(7)
                            player._tonBalance -= CVAR.transactionFee
                            player.spendToken(amount)
                        } else {
                            GVAR.showFloatingText(29);
                        }
                    } else {
                        GVAR.showFloatingText(2);
                    }
                } else {
                    GVAR.showFloatingText(23);
                }
            } else {
                GVAR.showFloatingText(28);
            }
        }

    }
    close(){
        document.getElementById("withdraw-menu-wrap").style.display = "none";
        document.getElementById("main-menu-wrap").style.display = "flex";
    }
    show() {
        GVAR.closeAllWindows();
        document.getElementById("withdraw-menu-wrap").style.display = "flex";
        this.drawMenu();
    }
    drawMenu() {
        document.getElementById('withdraw-ton-balance').innerText = (player._tonBalance / 1000000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        document.getElementById('withdraw-token-balance').innerText = (player._tokenBalance / 100).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0];
        document.getElementById('withdraw-rule').innerText = GVAR.localization[24][GVAR.language]
        document.getElementById('withdraw-adress-text').innerText = GVAR.localization[25][GVAR.language]
        document.getElementById('withdraw-amount-text').innerText = GVAR.localization[26][GVAR.language]
        document.getElementById('confirm-withdraw-text').innerText = GVAR.localization[27][GVAR.language]
    }    
}

export const withdraw = new WithdrawMenu();