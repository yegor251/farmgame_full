import player from "../player/player.js";
import GVAR from "../../globalVars/global.js";
import socketClient from "../../init.js";
import CVAR from "../../globalVars/const.js";
import Calc from "../../calc.js";

class Orders {
    constructor() {
        this.renderOrders();
        document.getElementById("closeOrders").onclick = () => {
            this.close()
        }
        document.getElementById("orders-wrap").onclick = (e) => {
            if (e.target == document.getElementById("orders-wrap"))
                this.close()
        };
        this.chosenOrderInd = 'none'
    }
    clear(){
        document.getElementById('order-details').innerHTML = "";
        document.getElementById('order-buttons-bar').innerHTML = "";
        document.getElementById('order-money-content').style.display = "none";
        document.getElementById('order-token-content').style.display = "none";
    }
    close(){
        this.chosenOrderInd = 'none'
        clearInterval(this._intervalId)
        document.getElementById("orders-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
    show(){
        document.getElementById("orders-wrap").style.display = "flex";
        this.chosenOrderInd = 'none'
        this.clear()
        this._intervalId = setInterval(() => {
            if (this.chosenOrderInd != 'none'){
                this.showOrderDetails()
                this.renderOrders();
            }
        }, 1000);
        this.renderOrders();
    }
    verifyOrder(order) {
        for (let item in order.orderItems) {
            if (order.orderItems[item] > player._inventory[item]) return false;
        }
        return true;
    }
    completeOrder(order) {
        if (this.verifyOrder(order)) {
            order.timeStamp = Math.floor(Date.now()/1000) + CVAR.orderCompleteTime
            socketClient.send(`order/complete/${order.index}`)
            socketClient.send(`regen`)
            this.showTimer(order);
            this.renderOrders();
            this.clear()
            GVAR.showFloatingText(7)
        }
    }
    rerollOrder(order){
        order.timeStamp = Math.floor(Date.now()/1000) + CVAR.orderRerollTime
        socketClient.send(`order/reroll/${this.chosenOrderInd}`)
        socketClient.send(`regen`)
        this.showTimer(order);
        this.renderOrders()
        this.clear()
    }
    showTimer(order){
        this.clear()
        const orderDetails = document.getElementById('order-details');
        const timer = document.createElement('h3')
        timer.className = 'order-timer'
        orderDetails.appendChild(timer)
        if (order.timeStamp > Math.floor(Date.now()/1000))
            timer.innerText = Calc.formatTime(order.timeStamp - Math.floor(Date.now()/1000))
        else
            this.showOrderDetails()
    }
    showOrderDetails() {
        const order = player._orderArr[this.chosenOrderInd]
        if (order.timeStamp > Math.floor(Date.now()/1000)){
            this.showTimer(order)
            return
        }
        document.getElementById('order-money-content').style.display = "flex";
        document.getElementById('order-token-content').style.display = "flex";
        const orderDetails = document.getElementById('order-details');
        orderDetails.innerHTML = "";

        const orderPrice = document.getElementById('order-money');
        orderPrice.innerText = order.orderPrice

        const orderTokenPrice = document.getElementById('order-token');
        orderTokenPrice.innerText = (order.orderTokenPrice / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0]

        for (let item in order.orderItems) {
            const res = document.createElement("div");
            res.className = "order-res";

            const resImg = document.createElement("div");
            resImg.style.backgroundImage = `url('client/assets/items/${item}.png')`;
            resImg.className = "order-res-img";

            const amount = document.createElement("h3");
            amount.innerText = `${player._inventory[item]}/${order.orderItems[item]}`;
            amount.className = 'order-res-amount'
            if (player._inventory[item] >= order.orderItems[item])
                amount.classList.add("unlocked")
            else
                amount.classList.add("locked")

            res.appendChild(resImg);
            res.appendChild(amount);
            orderDetails.appendChild(res);
        }

        const completeButton = document.createElement("div");
        completeButton.className = `complete-order`;
        if (this.verifyOrder(order))
            completeButton.onclick = () => {
                GVAR.canRerollOrders = true
                this.completeOrder(order);
            };
        else
            completeButton.style.filter = 'grayscale(100%)';

        const rerollButton = document.createElement("div");
        rerollButton.className = `reroll-order`;
        rerollButton.onclick = () => {
            if (GVAR.canRerollOrders) {
                if (GVAR.confirmFlag)
                    this.rerollOrder(order);
                else {
                    GVAR.setConfirm()
                    GVAR.showFloatingText(4)
                }
            }
        };
        document.getElementById('order-buttons-bar').innerHTML = ''
        document.getElementById('order-buttons-bar').appendChild(completeButton)
        document.getElementById('order-buttons-bar').appendChild(rerollButton)
    }
    renderOrders() {
        const ordersList = document.getElementById('orders-list');
        ordersList.innerHTML = "";
        for (let i in player._orderArr) {
            const ord = player._orderArr[i];
            ord.index = i
            const order = document.createElement("div");
            order.className = "order";
            if (ord.timeStamp > Math.floor(Date.now()/1000))
                order.style.backgroundImage = `url(client/assets/design/order_wait${i % 3}.png)`;
            else
                order.style.backgroundImage = `url(client/assets/design/order${i % 3}.png)`;
            order.onclick = () => {
                GVAR.deleteConfirm()
                this.chosenOrderInd = i
                this.showOrderDetails();
            };

            ordersList.appendChild(order);
        }
    }
}

export const orderManager = new Orders();
