import player from "../player/player.js";
import GVAR from "../../globalVars/global.js";
import mouse from "../controller/mouse.js";
import Calc from "../../calc.js";
import CVAR from "../../globalVars/const.js";
import RES from "../../resources.js";
import Phantom from "../sprite/phantom.js";
import socketClient from "../../init.js";

class Shop{
    constructor() {
        const shopWrap = document.getElementById('shop-wrap');
        shopWrap.onclick = (e) => {
            if (e.target == shopWrap || e.target == document.getElementById("shop-list") 
             || e.target == document.getElementById("shop") || 
             e.target == document.getElementById("shop-wrap")){
                const slidableDiv = document.getElementById('shop');
                slidableDiv.classList.add('slide-out');
                setTimeout(() => {
                    document.getElementById("shop-wrap").style.display = "none";
                    document.getElementById("open-shop").style.display = "flex";
                    document.getElementById("open-main-menu").style.display = "flex";
                    document.getElementById("open-manual").style.display = "flex";
                }, 450);
             }
        }
        
        const categories = [
            { name: 'building', method: 'drawBuildingShop' },
            { name: 'plant', method: 'drawPlantShop' },
            { name: 'animal', method: 'drawAnimalShop' },
            { name: 'animalPen', method: 'drawAnimalPenShop' },
            { name: 'bush', method: 'drawBushShop' },
        ];
        
        categories.forEach(category => {
            const buyButton = document.createElement('div');
            buyButton.id = `buy-${category.name}`;
            buyButton.className = 'shop-categorie';
        
            const icon = document.createElement('div');
            icon.className = 'shop-categorie-icon';
            icon.style.backgroundImage = `url('client/assets/design/${category.name}_icon.png')`;
            buyButton.appendChild(icon);
        
            document.getElementById('shop-bar').appendChild(buyButton);
        
            buyButton.onclick = () => {
                this[category.method]();
            };
        });        
    
        document.getElementById("open-shop").onclick = () => {
            this.show()
        }        

        document.getElementById("closeStash").onclick = () => {
            this.closeStash()
        }
        document.getElementById("stash-wrap").onclick = (e) => {
            if (e.target == document.getElementById("stash-wrap"))
                this.closeStash()
        };
        const upgButton = document.getElementById('upgrade-stash-button')
        upgButton.onclick = () => {
            document.getElementById('selection-menu-wrap').style.display = 'flex'
            document.getElementById('selection-text').innerText = GVAR.localization[35][GVAR.language].replace(/\{/g, player._inventorySize < 120 ? 1 : 10)
            document.getElementById('selection-yes').onclick = () => {
                if (player._tokenBalance >= player.getUpgInvPrice() && player._inventorySize < CVAR.maxInvSize){
                    player.upgradeInventory()
                    socketClient.send('invupgrade')
                    this.drawStash()
                    GVAR.showFloatingText(7)
                } else {
                    GVAR.showFloatingText(2)
                }
                document.getElementById('selection-menu-wrap').style.display = 'none'
            }
        }
        upgButton.innerText = GVAR.localization[8][GVAR.language]
    }
    show(){
        const slidableDiv = document.getElementById('shop');
        slidableDiv.classList.remove('slide-out');
        GVAR.closeAllWindows();
        document.getElementById("shop-wrap").style.display = "flex";
        this.drawBuildingShop();
    }
    drawBuildingShop(){
        const shop = document.getElementById('shop-list');
        shop.innerHTML = '';
        RES.buildingNames.garden.concat(RES.buildingNames.bakery).forEach(building => {
            const itemContent = document.createElement('div');
            const shopItem = document.createElement('div');
            const content = document.createElement('div');
            content.className = 'shop-item-content'
            const img = document.createElement('div');
            img.style.backgroundImage = `url('client/assets/buildings/${building}/${building}.png')`;
            img.className = 'shop-item-img'
            const priceWithArrow = document.createElement('div');
            priceWithArrow.className = 'price-with-arrow';
            const price = document.createElement('h3');
            price.innerText = `${RES.buildings[building].price}$`;
            price.className = 'shop-item-price'
            const priceContainer = document.createElement('div');
            priceContainer.className = 'shop-price-container'
            priceContainer.appendChild(price)
    
            const descriptionMenu = document.createElement('div');
            descriptionMenu.className = 'description-menu';
            descriptionMenu.style.display = 'none';
            const description = document.createElement('h3')
            description.className = 'description'
            description.innerHTML = RES.buildings[building].localization.description[GVAR.language]
            descriptionMenu.appendChild(description)
    
            const arrow = document.createElement('span');
            arrow.innerText = '↓';
            arrow.className = 'description-arrow';
    
            priceWithArrow.addEventListener('click', function(event) {
                if (descriptionMenu.style.display === 'none') {
                    descriptionMenu.style.display = 'block';
                    arrow.innerText = '↑';
                } else {
                    descriptionMenu.style.display = 'none';
                    arrow.innerText = '↓';
                }
            }) 
            descriptionMenu.addEventListener('click', function() {
                descriptionMenu.style.display = 'none';
                arrow.innerText = '↓';
            }) 

            priceWithArrow.appendChild(priceContainer)
            priceWithArrow.appendChild(arrow)
            content.appendChild(img);
            content.appendChild(priceWithArrow);
            shopItem.appendChild(content)
            itemContent.appendChild(shopItem)
            itemContent.appendChild(descriptionMenu)
    
            if (GVAR.countBuilding(building) < RES.buildings[building].mapLimit && player._money >= RES.buildings[building].price) {
                let touchStartX = 0;
                let touchStartY = 0;
                let isScrolling = false;
                let touchTimer = null;

                img.addEventListener("touchstart", function(e) {
                    touchStartX = e.touches[0].clientX;
                    touchStartY = e.touches[0].clientY;
                    isScrolling = false;

                    touchTimer = setTimeout(function() {
                        if (!isScrolling) {
                            document.getElementById("shop-wrap").style.display = "none";
                            document.getElementById("open-shop").style.display = "flex";
                            document.getElementById("open-main-menu").style.display = "flex";
                            document.getElementById("open-manual").style.display = "flex";
                            player._phantomStructure = {
                                cost: RES.buildings[building].price,
                                structureType: 'building'
                            };
                            let pos = Calc.indexToCanvas(mouse._mapPos.i, mouse._mapPos.j, CVAR.tileSide, CVAR.outlineWidth);
                            player._phantomStructure.structure = new Phantom(pos.x, pos.y, RES.buildings[building].size, building, RES.buildings[building].image);
                            player._phantomStructure.structure._isMoving = true;
                            GVAR.phantomStructureArr.push(player._phantomStructure.structure);
                            mouse._isDragging = true;
                            mouse._isBlockAfterShop = true;
                            setTimeout(() => {
                                mouse._isBlockAfterShop = false
                            }, 1000);

                            if (building == 'garden' && GVAR.countBuilding('garden') == 0){
                                const customEvent = new Event('firstGarden');
                                document.body.dispatchEvent(customEvent);
                            }
                            if (building == 'bakery' && GVAR.countBuilding('bakery') == 0){
                                const customEvent = new Event('firstBuilding');
                                document.body.dispatchEvent(customEvent);
                            }
                            mouse.onMouseMove(e);
                        }
                    }, 300);
                });

                img.addEventListener("touchmove", function(e) {
                    let touchMoveX = e.touches[0].clientX;
                    let touchMoveY = e.touches[0].clientY;

                    if (Math.abs(touchMoveX - touchStartX) > 10 || Math.abs(touchMoveY - touchStartY) > 10) {
                        isScrolling = true;
                        clearTimeout(touchTimer);
                    }
                });

                img.addEventListener("touchend", function(e) {
                    clearTimeout(touchTimer);
                });

            } else {
                img.style.filter = 'grayscale(100%)';
            }
    
            shopItem.className = "shop-item";
            shop.appendChild(itemContent);
        });
    }    
    drawPlantShop(){
        const shop = document.getElementById('shop-list');
        shop.innerHTML = '';
        RES.names.plants.forEach(plant => {
            const itemContent = document.createElement('div');
            const shopItem = document.createElement('div');
            const content = document.createElement('div');
            content.className = 'shop-item-content'
            const img = document.createElement('div');
            img.style.backgroundImage = `url('client/assets/items/${plant}.png')`;
            img.className = 'shop-item-img'
            const priceWithArrow = document.createElement('div');
            priceWithArrow.className = 'price-with-arrow';
            const price = document.createElement('h3');
            price.innerText = `${RES.plants[plant].seed.price}$`;
            price.className = 'shop-item-price'
            const priceContainer = document.createElement('div');
            priceContainer.className = 'shop-price-container'
            priceContainer.appendChild(price)

            const descriptionMenu = document.createElement('div');
            descriptionMenu.className = 'description-menu';
            descriptionMenu.style.display = 'none';
            const description = document.createElement('h3')
            description.className = 'description'
            description.innerHTML = RES.plants[plant].localization.description[GVAR.language]
            descriptionMenu.appendChild(description)

            const arrow = document.createElement('span');
            arrow.innerText = '↓';
            arrow.className = 'description-arrow';
    
            priceWithArrow.addEventListener('click', function(event) {
                if (descriptionMenu.style.display === 'none') {
                    descriptionMenu.style.display = 'block';
                    arrow.innerText = '↑';
                } else {
                    descriptionMenu.style.display = 'none';
                    arrow.innerText = '↓';
                }
            }) 
            descriptionMenu.addEventListener('click', function() {
                descriptionMenu.style.display = 'none';
                arrow.innerText = '↓';
            }) 

            priceWithArrow.appendChild(priceContainer)
            priceWithArrow.appendChild(arrow)
            content.appendChild(img);
            content.appendChild(priceWithArrow);
            shopItem.appendChild(content)
            itemContent.appendChild(shopItem)
            itemContent.appendChild(descriptionMenu)

            if (player._money < RES.plants[plant].seed.price)
                img.style.filter = 'grayscale(100%)';
            img.onclick = () => {
                if (player._money < RES.plants[plant].seed.price){
                    GVAR.showFloatingText(1)
                    return
                }
                if (player.getInvFullness() == 0){
                    GVAR.showFloatingText(3)
                    return
                }
                player.buy(RES.plants[plant].seed.price)
                player.pushInventory(plant, 1)
                GVAR.showFloatingItem(1, plant, {x: window.innerWidth / 2, y: window.innerHeight / 2})
                socketClient.send(`buy/${plant}/${1}`)
                this.drawPlantShop()
            }
            shopItem.className = "shop-item";
            shop.appendChild(itemContent);
        });
    }
    drawAnimalShop(){
        const shop = document.getElementById('shop-list');
        shop.innerHTML = '';
        RES.names.animals.forEach(animal => {
            const itemContent = document.createElement('div');
            const shopItem = document.createElement('div');
            const content = document.createElement('div');
            content.className = 'shop-item-content'
            const img = document.createElement('div');
            img.style.backgroundImage = `url('client/assets/animals/${animal}/${animal}.png')`;
            img.className = 'shop-item-img'
            const priceWithArrow = document.createElement('div');
            priceWithArrow.className = 'price-with-arrow';
            const price = document.createElement('h3');
            price.innerText = `${RES.animals[animal].price}$`;
            price.className = 'shop-item-price'
            const priceContainer = document.createElement('div');
            priceContainer.className = 'shop-price-container'
            priceContainer.appendChild(price)

            const descriptionMenu = document.createElement('div');
            descriptionMenu.className = 'description-menu';
            descriptionMenu.style.display = 'none';
            const description = document.createElement('h3')
            description.className = 'description'
            description.innerHTML = RES.animals[animal].localization.description[GVAR.language]
            descriptionMenu.appendChild(description)
    
            const arrow = document.createElement('span');
            arrow.innerText = '↓';
            arrow.className = 'description-arrow';
    
            priceWithArrow.addEventListener('click', function(event) {
                if (descriptionMenu.style.display === 'none') {
                    descriptionMenu.style.display = 'block';
                    arrow.innerText = '↑';
                } else {
                    descriptionMenu.style.display = 'none';
                    arrow.innerText = '↓';
                }
            }) 
            descriptionMenu.addEventListener('click', function() {
                descriptionMenu.style.display = 'none';
                arrow.innerText = '↓';
            }) 

            priceWithArrow.appendChild(priceContainer)
            priceWithArrow.appendChild(arrow)
            content.appendChild(img);
            content.appendChild(priceWithArrow);
            shopItem.appendChild(content)
            itemContent.appendChild(shopItem)
            itemContent.appendChild(descriptionMenu)

            if (player._money >= RES.animals[animal].price){
                let touchStartX = 0;
                let touchStartY = 0;
                let isScrolling = false;
                let touchTimer = null;

                img.addEventListener("touchstart", function(e) {
                    touchStartX = e.touches[0].clientX;
                    touchStartY = e.touches[0].clientY;
                    isScrolling = false;

                    touchTimer = setTimeout(function() {
                        if (!isScrolling) {
                            document.getElementById("shop-wrap").style.display = "none";
                            document.getElementById("open-shop").style.display = "flex";
                            document.getElementById("open-main-menu").style.display = "flex";
                            document.getElementById("open-manual").style.display = "flex";
                            player._phantomStructure = {
                                cost: RES.animals[animal].price,
                                structureType: 'animal'
                            };
                            let pos = Calc.indexToCanvas(mouse._mapPos.i, mouse._mapPos.j, CVAR.tileSide, CVAR.outlineWidth);
                            player._phantomStructure.structure = new Phantom(pos.x, pos.y, RES.animals[animal].size, animal, RES.animals[animal].standImages[0]);
                            player._phantomStructure.structure._isMoving = true;
                            GVAR.phantomStructureArr.push(player._phantomStructure.structure);
                            mouse._isDragging = true;
                            mouse._isBlockAfterShop = true;
                            setTimeout(() => {
                                mouse._isBlockAfterShop = false
                            }, 1000);
                            mouse.onMouseMove(e);
                        }
                    }, 300);
                });

                img.addEventListener("touchmove", function(e) {
                    let touchMoveX = e.touches[0].clientX;
                    let touchMoveY = e.touches[0].clientY;

                    if (Math.abs(touchMoveX - touchStartX) > 10 || Math.abs(touchMoveY - touchStartY) > 10) {
                        isScrolling = true;
                        clearTimeout(touchTimer);
                    }
                });

                img.addEventListener("touchend", function(e) {
                    clearTimeout(touchTimer);
                });
            } else {
                img.style.filter = 'grayscale(100%)';
            }
            shopItem.className = "shop-item";
            shop.appendChild(itemContent);
        });
    }
    drawAnimalPenShop(){
        const shop = document.getElementById('shop-list');
        shop.innerHTML = '';
        RES.buildingNames.animalPen.forEach(building => {
            const itemContent = document.createElement('div');
            const shopItem = document.createElement('div');
            const content = document.createElement('div');
            content.className = 'shop-item-content'
            const img = document.createElement('div');
            img.style.backgroundImage = `url('client/assets/buildings/${building}/${building}.png')`;
            img.className = 'shop-item-img'
            const priceWithArrow = document.createElement('div');
            priceWithArrow.className = 'price-with-arrow';
            const price = document.createElement('h3');
            price.innerText = `${RES.buildings[building].price}$`;
            price.className = 'shop-item-price'
            const priceContainer = document.createElement('div');
            priceContainer.className = 'shop-price-container'
            priceContainer.appendChild(price)

            const descriptionMenu = document.createElement('div');
            descriptionMenu.className = 'description-menu';
            descriptionMenu.style.display = 'none';
            const description = document.createElement('h3')
            description.className = 'description'
            description.innerHTML = RES.buildings[building].localization.description[GVAR.language]
            descriptionMenu.appendChild(description)
    
            const arrow = document.createElement('span');
            arrow.innerText = '↓';
            arrow.className = 'description-arrow';
    
            priceWithArrow.addEventListener('click', function(event) {
                if (descriptionMenu.style.display === 'none') {
                    descriptionMenu.style.display = 'block';
                    arrow.innerText = '↑';
                } else {
                    descriptionMenu.style.display = 'none';
                    arrow.innerText = '↓';
                }
            }) 
            descriptionMenu.addEventListener('click', function() {
                descriptionMenu.style.display = 'none';
                arrow.innerText = '↓';
            }) 

            priceWithArrow.appendChild(priceContainer)
            priceWithArrow.appendChild(arrow)
            content.appendChild(img);
            content.appendChild(priceWithArrow);
            shopItem.appendChild(content)
            itemContent.appendChild(shopItem)
            itemContent.appendChild(descriptionMenu)

            if (player._money >= RES.buildings[building].price){
                let touchStartX = 0;
                let touchStartY = 0;
                let isScrolling = false;
                let touchTimer = null;

                img.addEventListener("touchstart", function(e) {
                    touchStartX = e.touches[0].clientX;
                    touchStartY = e.touches[0].clientY;
                    isScrolling = false;

                    touchTimer = setTimeout(function() {
                        if (!isScrolling) {
                            document.getElementById("shop-wrap").style.display = "none";
                            document.getElementById("open-shop").style.display = "flex";
                            document.getElementById("open-main-menu").style.display = "flex";
                            document.getElementById("open-manual").style.display = "flex";
                            player._phantomStructure = {
                                cost: RES.buildings[building].price,
                                structureType: 'building'
                            }
                            let pos = Calc.indexToCanvas(mouse._mapPos.i, mouse._mapPos.j, CVAR.tileSide, CVAR.outlineWidth)
                            player._phantomStructure.structure = new Phantom(pos.x, pos.y, RES.buildings[building].size, building, RES.buildings[building].image)
                            player._phantomStructure.structure._isMoving = true
                            GVAR.phantomStructureArr.push(player._phantomStructure.structure)
                            mouse._isDragging = true
                            mouse._isBlockAfterShop = true;
                            setTimeout(() => {
                                mouse._isBlockAfterShop = false
                            }, 1000);
                            mouse.onMouseMove(e)
                        }
                    }, 300);
                });

                img.addEventListener("touchmove", function(e) {
                    let touchMoveX = e.touches[0].clientX;
                    let touchMoveY = e.touches[0].clientY;

                    if (Math.abs(touchMoveX - touchStartX) > 10 || Math.abs(touchMoveY - touchStartY) > 10) {
                        isScrolling = true;
                        clearTimeout(touchTimer);
                    }
                });

                img.addEventListener("touchend", function(e) {
                    clearTimeout(touchTimer);
                });
            } else{
                img.style.filter = 'grayscale(100%)';
            }
            shopItem.className = "shop-item";
            shop.appendChild(itemContent);
        });
    }
    drawBushShop(){
        const shop = document.getElementById('shop-list');
        shop.innerHTML = '';
        RES.buildingNames.bush.forEach(building => {
            const itemContent = document.createElement('div');
            const shopItem = document.createElement('div');
            const content = document.createElement('div');
            content.className = 'shop-item-content'
            const img = document.createElement('div');
            img.style.backgroundImage = `url('client/assets/buildings/${building}/${building}1.png')`;
            img.className = 'shop-item-img'
            const priceWithArrow = document.createElement('div');
            priceWithArrow.className = 'price-with-arrow';
            const price = document.createElement('h3');
            price.innerText = `${RES.buildings[building].price}$`;
            price.className = 'shop-item-price'
            const priceContainer = document.createElement('div');
            priceContainer.className = 'shop-price-container'
            priceContainer.appendChild(price)

            const descriptionMenu = document.createElement('div');
            descriptionMenu.className = 'description-menu';
            descriptionMenu.style.display = 'none';
            const description = document.createElement('h3')
            description.className = 'description'
            description.innerHTML = RES.buildings[building].localization.description[GVAR.language]
            descriptionMenu.appendChild(description)
    
            const arrow = document.createElement('span');
            arrow.innerText = '↓';
            arrow.className = 'description-arrow';
    
            priceWithArrow.addEventListener('click', function(event) {
                if (descriptionMenu.style.display === 'none') {
                    descriptionMenu.style.display = 'block';
                    arrow.innerText = '↑';
                } else {
                    descriptionMenu.style.display = 'none';
                    arrow.innerText = '↓';
                }
            }) 
            descriptionMenu.addEventListener('click', function() {
                descriptionMenu.style.display = 'none';
                arrow.innerText = '↓';
            }) 

            priceWithArrow.appendChild(priceContainer)
            priceWithArrow.appendChild(arrow)
            content.appendChild(img);
            content.appendChild(priceWithArrow);
            shopItem.appendChild(content)
            itemContent.appendChild(shopItem)
            itemContent.appendChild(descriptionMenu)

            if (player._money >= RES.buildings[building].price){
                let touchStartX = 0;
                let touchStartY = 0;
                let isScrolling = false;
                let touchTimer = null;

                img.addEventListener("touchstart", function(e) {
                    touchStartX = e.touches[0].clientX;
                    touchStartY = e.touches[0].clientY;
                    isScrolling = false;

                    touchTimer = setTimeout(function() {
                        if (!isScrolling) {
                            document.getElementById("shop-wrap").style.display = "none";
                            document.getElementById("open-shop").style.display = "flex";
                            document.getElementById("open-main-menu").style.display = "flex";
                            document.getElementById("open-manual").style.display = "flex";
                            player._phantomStructure = {
                                cost: RES.buildings[building].price,
                                structureType: 'building'
                            }
                            let pos = Calc.indexToCanvas(mouse._mapPos.i, mouse._mapPos.j, CVAR.tileSide, CVAR.outlineWidth)
                            player._phantomStructure.structure = new Phantom(pos.x, pos.y, RES.buildings[building].size, building, RES.buildings[building].image[0])
                            player._phantomStructure.structure._isMoving = true
                            GVAR.phantomStructureArr.push(player._phantomStructure.structure)
                            mouse._isDragging = true
                            mouse._isBlockAfterShop = true;
                            setTimeout(() => {
                                mouse._isBlockAfterShop = false
                            }, 1000);
                            mouse.onMouseMove(e)
                        }
                    }, 300);
                });

                img.addEventListener("touchmove", function(e) {
                    let touchMoveX = e.touches[0].clientX;
                    let touchMoveY = e.touches[0].clientY;

                    if (Math.abs(touchMoveX - touchStartX) > 10 || Math.abs(touchMoveY - touchStartY) > 10) {
                        isScrolling = true;
                        clearTimeout(touchTimer);
                    }
                });

                img.addEventListener("touchend", function(e) {
                    clearTimeout(touchTimer);
                });
            } else{
                img.style.filter = 'grayscale(100%)';
            }
            shopItem.className = "shop-item";
            shop.appendChild(itemContent);
        });
    }
    drawStash()
    {
        document.getElementById("stash-wrap").style.display = "flex";
        const stashList = document.getElementById('stash-list')
        document.getElementById('stash-capacity-text').innerText = `${player._inventorySize - player.getInvFullness()}/${player._inventorySize}`
        stashList.innerHTML = "";
        const k = Math.trunc((player._inventorySize - player.getInvFullness()) * 10 / player._inventorySize)
        let n = 0
        if (k >= 8)
            n = 3
        else if (k >= 5)
            n = 2
        else if (k >= 1)
            n = 1
        const path = `url('client/assets/design/capacity_elem${n}.png`;
        document.getElementById('stash-capacity').innerHTML = ''
        for (let i = 0; i < k; i++) {
            const capElem = document.createElement('div')
            capElem.className = 'stash-capacity-elem'
            capElem.style.backgroundImage = path
            document.getElementById('stash-capacity').appendChild(capElem)
        }
        for (let i = k; i < 10; i++) {
            const capElem = document.createElement('div')
            capElem.className = 'stash-capacity-elem'
            capElem.style.backgroundImage = `url('client/assets/design/capacity_elem0.png`;
            document.getElementById('stash-capacity').appendChild(capElem)
        }

        const inventoryArray = Object.entries(player._inventory);
        inventoryArray.sort((a, b) => b[1] - a[1]);
        for (let [item] of inventoryArray)
        {
            if (player._inventory[item] > 0)
            {
                const div = document.createElement('div');
                div.className = 'stash-item'
                const img = document.createElement("div")
                img.style.backgroundImage = `url('client/assets/items/${item}.png')`;
                img.className = "stash-image"
                div.appendChild(img)

                const amount = document.createElement('h3');
                amount.innerHTML = player._inventory[item];  
                amount.className = 'stash-item-amount'  
                div.appendChild(amount);
                stashList.appendChild(div);
            }
        }
    }
    closeStash(){
        document.getElementById("stash-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
}
const shop = new Shop();
export default shop;
