import l from "../assets/localization/localization.js";
class GlobalVars{
    constructor()
    {
        this.buildableArr = new Array();
        this.penArr = new Array();
        this.phantomStructureArr = new Array(0);
        this.obstacleArr = new Array();

        this.scale = 7 * Math.max(window.innerWidth, window.innerHeight) / 1000;
        this.redraw = true;
        this.confirmFlag = false;
        this.confirmTimer = null
        this.localization = l.localization
        this.language = 'en'
        this.tg_id = ''
        this.tg_name = 'qwerty123'
        this.canRerollOrders = false
    }
    showBadCodeMenu(){
        document.getElementById("bad-code-wrap").style.display = "flex"
        const text = document.getElementById("relogin-text")
        text.innerText = this.localization[61][GVAR.language]
    }
    countBuilding(type){
        let counter = 0
        this.buildableArr.forEach(el => {
            if (el._type === type)
                counter += 1
        });
        return counter
    }
    addBuilding(item){
        let index = this.buildableArr.findIndex(element => element._y > item._y);
    
        if (index >= 0) {
            this.buildableArr.splice(index, 0, item);
        } else {
            this.buildableArr.push(item);
        }
    }
    updateBuildingArr(item) {
        let index = this.buildableArr.indexOf(item);
        
        if (index !== -1) {   
            this.buildableArr.splice(index, 1);
            this.addBuilding(item);
        }
    }
    closeAllWindows(){
        document.getElementById("spin-wrap").style.display = "none";
        document.getElementById("orders-wrap").style.display = "none";
        document.getElementById("stash-wrap").style.display = "none";
        document.getElementById("shop-wrap").style.display = "none";
        document.getElementById("building-menu-wrap").style.display = "none";
        document.getElementById("booster-menu-wrap").style.display = "none";
        document.getElementById("obstacle-menu-wrap").style.display = "none";
        document.getElementById("animal-menu-wrap").style.display = "none";
        document.getElementById("field-menu-wrap").style.display = "none";
        document.getElementById("bush-menu-wrap").style.display = "none";
        document.getElementById("transaction-wrap").style.display = "none";
        document.getElementById("deals-wrap").style.display = "none";
        document.getElementById("payment-wrap").style.display = "none";
        document.getElementById("main-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "none";
        document.getElementById("open-main-menu").style.display = "none";
        document.getElementById("open-manual").style.display = "none";
    }
    showFloatingText(code, text) {
        const existingTexts = document.querySelectorAll('.floating-text');
        let message = this.localization[code][this.language];
        if (message.includes('{')) {
            message = message.replace(/\{/g, text);
        }
        
        for (const textElement of existingTexts) {
            if (textElement.textContent === message && code != 22) {
                return;
            }
        }
    
        const textElement = document.createElement('div');
        textElement.textContent = message;
        textElement.classList.add('floating-text');
        
        document.body.appendChild(textElement);
      
        setTimeout(() => {
            textElement.classList.add('float-away');
        }, 50);
      
        setTimeout(() => {
            textElement.remove();
        }, 4000);
    }  
    showFloatingItem(amount, name, pos) {
        const content = document.createElement('div');
        content.style.left = pos.x + 'px'
        content.style.top = pos.y + 'px'
        content.classList.add('floating-item-box');
        const text = document.createElement('h3')
        text.innerText = '+' + amount
        const img = document.createElement('div')
        img.className = 'floating-item'
        img.style.backgroundImage = `url(client/assets/items/${name}.png)`
        content.appendChild(text)
        content.appendChild(img)
        
        document.body.appendChild(content);
      
        setTimeout(() => {
            content.classList.add('float-away');
        }, 50);
      
        setTimeout(() => {
            content.remove();
        }, 4000);
    }  
    setConfirm(){
        this.confirmFlag = true;
        this.confirmTimer = setTimeout(() => {
            this.confirmFlag = false;
        }, 3000);
    }
    deleteConfirm(){
        this.confirmFlag = false;
        clearTimeout(this.confirmTimer)
    }
}

const GVAR = new GlobalVars();

export default GVAR;