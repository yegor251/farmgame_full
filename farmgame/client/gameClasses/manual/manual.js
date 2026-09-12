import player from "../player/player.js";
import GVAR from "../../globalVars/global.js";
import RES from "../../resources.js";
import Calc from "../../calc.js";

class ManualMenu{
    constructor() {
        this.stack = []
        document.getElementById("close-manual").onclick = () => {
            this.close()
        }
        document.getElementById("manual-menu-wrap").onclick = (e) => {
            if (e.target == document.getElementById("manual-menu-wrap"))
                this.close()
        };
        document.getElementById("open-manual").onclick = (e) => {
            this.show()
        };
        document.getElementById("manual-back-button").onclick = (e) => {
            this.backStep()
        };
    }
    start(){
        const list = document.getElementById('manual-crafts-list');
        RES.names.items.forEach(name => {
            const cell = document.createElement('div')
            cell.className = 'manual-craft-cell'
            const img = document.createElement('div')
            img.className = 'manual-craft-img'
            img.style.backgroundImage = `url(client/assets/items/${name}.png)`
            cell.appendChild(img)
            list.appendChild(cell)
            cell.onclick = () => {
                this.clear()
                this.stack = []
                this.render(name)
            }
        });
    }
    render(name){
        if (RES.names.items.includes(name)) {
            this.renderBuild(name)
        } else if (RES.names.plants.includes(name)) {
            this.renderGarden(name)
        } else if (['egg', 'milk', 'wool', 'bacon'].includes(name)) {
            this.renderAnimal(name)
        } else if (['apple', 'raspberry', 'cherry', 'blackberry', 'strawberry'].includes(name)){
            this.renderBush(name)
        }
    }
    show(){
        this.clear()
        GVAR.closeAllWindows()
        document.getElementById('manual-menu-wrap').style.display = 'flex'
    }
    clear(){
        document.getElementById('manual-img-bar').innerHTML = ''
        document.getElementById('manual-items-list').innerHTML = ''
        document.getElementById('manual-time').innerText = ''
        document.getElementById('manual-back-button').style.display = 'none'
    }
    close(){
        document.getElementById("manual-menu-wrap").style.display = "none";
        document.getElementById("open-shop").style.display = "flex";
        document.getElementById("open-main-menu").style.display = "flex";
        document.getElementById("open-manual").style.display = "flex";
    }
    renderBuild(name) {
        const findName = (name) => {
            for (const building in RES.buildings) {
                if (RES.buildings[building].workTypes && RES.buildings[building].workTypes[name]){
                    return RES.buildings[building]
                }
            }
        }
        const imgBar = document.getElementById('manual-img-bar')
        const img = document.createElement('div')
        img.className = 'manual-big-img'
        imgBar.appendChild(img)
        const img1 = new Image();
        img1.onload = () => {
            img.style.backgroundImage = `url(client/assets/buildings/${building.name}/${building.name}.png)`;
            img.style.aspectRatio = `${img1.width} / ${img1.height}`;

            const imgAspectRatio = img1.width / img1.height;
            const width = window.innerWidth * 0.3466;
            const height = width / imgAspectRatio;
            imgBar.style.height = `${height}px`;
            itemsList.style.top = `${height + window.innerHeight * 0.05}px`;
        };
        const building = findName(name);
        img1.src = `client/assets/buildings/${building.name}/${building.name}.png`;

        const itemsList = document.getElementById('manual-items-list')

        for (const key in building.workTypes[name].items) {
            const cell = document.createElement('div')
            cell.className = 'manual-description-craft'

            const img = document.createElement('div')
            img.className = 'manual-description-img'
            img.style.backgroundImage = `url(client/assets/items/${key}.png)`
            cell.appendChild(img)
            const amount = document.createElement('h3')
            amount.className = 'manual-amount-text'
            amount.innerText = 'x' + building.workTypes[name].items[key]
            cell.appendChild(amount)

            const plus = document.createElement('div')
            plus.className = 'manual-plus'
            plus.innerText = '+'
            itemsList.appendChild(cell)
            itemsList.appendChild(plus)

            cell.onclick = () => {
                this.clear()
                document.getElementById('manual-back-button').style.display = 'flex'
                this.stack.push(name)
                this.render(key)
            }
        }
        itemsList.removeChild(itemsList.lastChild);

        document.getElementById('manual-time').innerText = Calc.formatTime(building.workTypes[name].timeToFinish)
    }
    renderGarden(name){
        const imgBar = document.getElementById('manual-img-bar')
        const img = document.createElement('div')
        img.className = 'manual-big-img'
        img.style.backgroundImage = `url(client/assets/buildings/garden/garden.png)`;
        img.style.aspectRatio = `1 / 1`;
        img.style.bottom = 0
        imgBar.appendChild(img)

        const plantImg = document.createElement('div')
        plantImg.className = 'manual-big-img'
        plantImg.style.backgroundImage = `url(client/assets/plants/${name}/${name}_stage3.png)`;
        imgBar.appendChild(plantImg)

        const img1 = new Image();
        img1.onload = () => {
            plantImg.style.aspectRatio = `${img1.width} / ${img1.height}`
            const imgAspectRatio = img1.width / img1.height;
            const width = window.innerWidth * 0.3466;
            const height = width / imgAspectRatio;
            imgBar.style.height = `${height}px`;
        };
        img1.src = `client/assets/plants/${name}/${name}_stage3.png`;
        document.getElementById('manual-time').innerText = Calc.formatTime(RES.plants[name].seed.timeToGrow)
    }
    renderAnimal(name){
        const pens = {
            egg: 'coop',
            milk: 'cowshed',
            bacon: 'pigsty',
            wool: 'sheepfold',
        }
        const buildName = pens[name]
        const building = RES.buildings[buildName]

        const itemsList = document.getElementById('manual-items-list')
        const imgBar = document.getElementById('manual-img-bar')
        const img = document.createElement('div')
        img.className = 'manual-big-img'
        imgBar.appendChild(img)
        img.style.backgroundImage = `url(client/assets/buildings/${building.name}/${building.name}.png)`;
        img.style.aspectRatio = `${building.image.width} / ${building.image.height}`;

        const imgAspectRatio = building.image.width / building.image.height;
        const width = window.innerWidth * 0.3466;
        const height = width / imgAspectRatio;
        imgBar.style.height = `${height}px`;
        itemsList.style.top = `${height + window.innerHeight * 0.05}px`;

        const animalImg = document.createElement('div')
        animalImg.className = 'manual-animal-img'
        animalImg.style.backgroundImage = `url(client/assets/animals/${building.animal}/${building.animal}.png)`;
        animalImg.style.aspectRatio = `${building.image.width} / ${building.image.height}`
        imgBar.appendChild(animalImg)

        const cell = document.createElement('div')
        cell.className = 'manual-description-craft'

        const feedImg = document.createElement('div')
        const feedType = Object.keys(building.intake)[0]
        feedImg.className = 'manual-description-img'
        feedImg.style.backgroundImage = `url(client/assets/items/${feedType}.png)`
        cell.appendChild(feedImg)
        const amount = document.createElement('h3')
        amount.className = 'manual-amount-text'
        amount.innerText = '1:1'
        cell.appendChild(amount)
        cell.onclick = () => {
            this.clear()
            document.getElementById('manual-back-button').style.display = 'flex'
            this.stack.push(name)
            this.render(feedType)
        }
        itemsList.appendChild(cell)
        document.getElementById('manual-time').innerText = Calc.formatTime(building.speed)
    }
    renderBush(name){
        const bushes = {
            apple: 'apple_tree',
            raspberry: 'raspberry',
            cherry: 'cherry',
            blackberry: 'blackberry',
            strawberry: 'strawberry',
        }
        const bushName = bushes[name]
        const bush = RES.buildings[bushName]

        const itemsList = document.getElementById('manual-items-list')
        const imgBar = document.getElementById('manual-img-bar')
        const img = document.createElement('div')
        img.className = 'manual-big-img'
        imgBar.appendChild(img)
        img.style.backgroundImage = `url(client/assets/buildings/${bush.name}/${bush.name}1.png)`;
        img.style.aspectRatio = `${bush.image[1].width} / ${bush.image[1].height}`;

        img.style.top = `${window.innerHeight * 0.1}px`;

        const imgAspectRatio = bush.image[1].width / bush.image[1].height;
        const width = window.innerWidth * 0.3466;
        const height = width / imgAspectRatio;
        imgBar.style.height = `${height + window.innerHeight * 0.1}px`;
        itemsList.style.top = `${height + window.innerHeight * 0.05}px`;

        document.getElementById('manual-time').innerText = Calc.formatTime(bush.speed)
    }
    backStep(){
        const name = this.stack.pop()
        this.clear()
        if (this.stack.length == 0)
            document.getElementById('manual-back-button').style.display = 'none'
        else
            document.getElementById('manual-back-button').style.display = 'flex'
        this.render(name)
    }
}
export const manualMenu = new ManualMenu();
