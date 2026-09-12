import RES from "./resources.js";
import tiles from "./globalVars/tiles.js";
import Calc from "./calc.js";
import CVAR from "./globalVars/const.js";
import player from "./gameClasses/player/player.js";
import GVAR from "./globalVars/global.js";
import loader from "./loadingScreen.js";
import { spin } from "./gameClasses/spin/spin.js";

class SocketClient{
    constructor()
    {
        this.requestQueue = new Array()
        const wsProtocol = window.location.protocol === 'https' ? 'wss' : 'ws';
        this.socket = new WebSocket(`${wsProtocol}://${window.location.hostname}:8000`);
        this.gameSessionPromiseResolve = null;
        this.gameSessionPromise = new Promise((resolve) => {
            this.gameSessionPromiseResolve = resolve;
        });
        this.interval = setInterval(() => {
            this.send('ping')
        }, 50000);
        this.socket.onmessage = (m) => {
            const data = JSON.parse(m.data)
            console.log(data)

            if (data.dataType == "game-session") 
            {
                this.initGameSession(data)
            }
            else if (data.dataType == "game-session-regen")
            {
                this.regenPlayer(data)
            }
            else if (data.dataType == "result-code")
            {
                this.handleResultCode(data.code)
            }
        }
    }
    _decipherRequest(request) {
        let parts = request.split('/');

        let requestType = parts[0];
        let result = { requestType: requestType };

        switch (requestType) {
            case 'connect':
                result.text = parts[1];
                break;
            case 'use':
                result.name = parts[1];
                result.x = parseInt(parts[2]);
                result.y = parseInt(parts[3]);
                break;
            case 'collect':
                result.x = parseInt(parts[1]);
                result.y = parseInt(parts[2]);
                break;
            case 'upgrade':
                result.x = parseInt(parts[1]);
                result.y = parseInt(parts[2]);
                break;
            case 'buy':
                result.name = parts[1];
                result.amount = parseInt(parts[2]);
                break;
            case 'spin':
                break;
            case 'regen':
                break;
            case 'order':
                result.operation = parts[1];
                result.index = parseInt(parts[2]);
                break;
            case 'place':
                result.name = parts[1];
                result.x = parseInt(parts[2]);
                result.y = parseInt(parts[3]);
                break;
            case 'move':
                result.x = parseInt(parts[1]);
                result.y = parseInt(parts[2]);
                result.to_x = parseInt(parts[3]);
                result.to_y = parseInt(parts[4]);
                break;
            case 'claim':
                result.index = parseInt(parts[1]);
                break;
            case 'withdraw':
                result.amount = parseFloat(parts[1]);
                break;
            case 'buyslot':
                result.x = parseInt(parts[1]);
                result.y = parseInt(parts[2]);
                break;
            case 'buydeal':
                result.name = parts[1];
                break;
            case 'activateb':
                result.index = parseInt(parts[1]);
                break;
            case 'invupgrade':
                break;
            default:
                result = { requestType: 'Unknown' };
                break;
        }

        return result;
    }
    handleResultCode(code){
        console.log(this.requestQueue[0])
        if (code == 200){
            let request = this._decipherRequest(this.requestQueue[0])
            if (request.requestType == 'use') {
                tiles[request.x][request.y].use(request.name)
            } else if (request.requestType == 'activateb'){
                player.realActivateBooster()
            } else if (request.requestType == 'place' && RES.buildingNames.bush.includes(request.name)){
                tiles[request.x][request.y].use()
            }
        }
        if (code != 200 && this.requestQueue[0] != 'ping')
            GVAR.showBadCodeMenu()
        console.log('код',code)
        this.requestQueue.shift()
    }
    send(request) {
        console.log('send')
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(request);
            if (request.split('/')[0] != 'connect' && request.split('/')[0] != 'regen'){
                this.requestQueue.push(request);
            }
            console.log(this.requestQueue)
        } else {
            GVAR.showBadCodeMenu()
            console.log('отключился сокет')
            location.reload();
        }
    }
  	regenPlayer(data){
		player._inventory = data.player.Inventory.map
        player._inventorySize = 70 + 10 * data.player.Inventory.level
		player._money = data.player.money
        player._networth = data.player.networth
        player._tokenBalance = data.wallet.tokenBalance
        player.updateMoney()
        player._tonBalance = data.wallet.tonBalance
        player._usdtBalance = data.wallet.usdtBalance

        player._spinItems = data.player.spin.items
        player._isSpinActivated = data.player.spin.activated
        player._spinTimeStamp = data.player.spin.generateTimeStamp
        for (let i = 0; i < player._spinItems.length; i++) {
            const el = player._spinItems[i];
            if (el.item == data.player.spin.drop.item && el.amount == data.player.spin.drop.amount){
                player._spinDropIndex = i
                break
            }
        }
        spin.renderSpin()
      	player._orderArr = data.player.orders
        player._boostersArr = []
        data.availableBoosters.forEach(el => {
            const booster = {
                type: el.boosterType,
                time: el.time
            }
            if (el.boosterType == "GrowSpeed" || el.boosterType == "WorkSpeed"){
                booster.amount = 100 / (100 - el.percentage)
            } else if (el.boosterType == "OrderMoney"){
                booster.amount = el.percentage / 100 + 1
            } else if (el.boosterType == "OrderItems"){
                booster.amount = el.percentage / 100
            }
            player._boostersArr.push(booster)
        });

        player._activBoostersArr = []
        for (const key in data.activeBoosters) {
            if (key == 'WorkSpeed'){
                player._workBooster.boosterAmount = 100 / (100 - data.activeBoosters[key].percentage)
                player._workBooster.timeStamp = (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000
                player._workBooster.timeToEnd = player._workBooster.timeStamp - Date.now()
                player._activBoostersArr.push(player._workBooster)
            } else if (key == 'GrowSpeed'){
                player._growBooster.boosterAmount = 100 / (100 - data.activeBoosters[key].percentage)
                player._growBooster.timeStamp = (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000
                player._growBooster.timeToEnd = player._growBooster.timeStamp - Date.now()
                player._activBoostersArr.push(player._growBooster)
            } else if (key == 'OrderMoney'){
                const booster = {
                    type: 'OrderMoney',
                    boosterAmount: data.activeBoosters[key].percentage / 100 + 1,
                    timeStamp: (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000,
                    timeToEnd: (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000 - Date.now()
                }
                player._activBoostersArr.push(booster)
            } else if (key == 'OrderItems'){
                const booster = {
                    type: 'OrderItems',
                    boosterAmount: data.activeBoosters[key].percentage / 100,
                    timeStamp: (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000,
                    timeToEnd: (data.activeBoosters[key].activateTimeStamp + data.activeBoosters[key].time) * 1000 - Date.now()
                }
                player._activBoostersArr.push(booster)
            } 
        }
  	}
  	initGameSession(data){
    	console.log(data)
        this.regenPlayer(data)
      	data.world.tileArray.forEach(el => {
          	tiles[el.x][el.y].createBuilding(el.name)
          	if (RES.buildingNames.bakery.includes(el.name)){
              	el.slots.forEach(slot => {
                  	tiles[el.x][el.y]._structure.addSlot(slot)
              	});
                tiles[el.x][el.y]._structure._level = el.level
              	tiles[el.x][el.y]._structure._slotsAmount += el.integerData
          	} else if (RES.buildingNames.garden.includes(el.name)){
				if (el.slots[0].workName != 'none')
					tiles[el.x][el.y]._structure.addSlot(el.slots[0])
			} else if (RES.buildingNames.animalPen.includes(el.name)){
				for (let i = 0; i < el.integerData; i++) {
					tiles[el.x][el.y]._structure.addAnimal()
				}
                tiles[el.x][el.y]._structure.setLevel(el.level)
				if (el.slots[0])
					tiles[el.x][el.y]._structure.setTime(el.slots[0].workEndTimeStamp)
			} else if (RES.buildingNames.bush.includes(el.name)){
				tiles[el.x][el.y]._structure.setProperties(el.slots[0].workEndTimeStamp, el.integerData)
			}
		});
        RES.buildingNames.bakery.concat(RES.buildingNames.animalPen).forEach(name => {
            RES.buildings[name].price *= Math.pow(CVAR.nextBuildingPriceCoef, GVAR.countBuilding(name))
        });
        RES.buildings['garden'].floatPrice = RES.buildings['garden'].price * Math.pow(CVAR.nextGardenPriceCoef, GVAR.countBuilding('garden'))
        RES.buildings['garden'].price = Math.floor(RES.buildings['garden'].floatPrice)

        player._availableDeals = data.availableDeals

        let transactions = [
            ...data.deposits.map((dep, index) => ({
                ...dep,
                time_stamp: Math.round(dep.time_stamp),
                type: 'dep',
                index
            })),
            ...data.withdraws.map(wit => ({
                ...wit,
                time_stamp: Math.round(wit.time_stamp),
                type: 'wit',
                jetton_signature: 'TFC'
            }))
        ];        

        transactions.sort((a, b) => b.time_stamp - a.time_stamp);

        player._transactions = transactions;

		this.gameSessionPromiseResolve()
  	}
}

const socketClient = new SocketClient();

export default socketClient;

class Init {
    constructor() {
        if (Object.keys(window.Telegram.WebApp.initDataUnsafe).length != 0){
            window.Telegram.WebApp.expand();
            window.Telegram.WebApp.disableVerticalSwipes();
            GVAR.tg_id = window.Telegram.WebApp.initDataUnsafe.user.id
            GVAR.tg_name = window.Telegram.WebApp.initDataUnsafe.user.username
            console.log(window.Telegram.WebApp.initDataUnsafe.user.language_code)
            if (window.Telegram.WebApp.initDataUnsafe.user.language_code === 'ru') {
                GVAR.language = 'ru'
            } else {
                GVAR.language = 'en'
            }
        }
    }
    async initMap(){
        loader.updateLoading(loader.progress, 'Initializing map')
        const Tile = (await import("./gameClasses/tile/tile.js")).default;
        
        for (let i = 0; i < CVAR.tileRows; i++) {
            tiles[i] = new Array(CVAR.tileCols);
        }
        for (let i = 0; i < CVAR.tileRows; i++)
        {
            for (let j = 0; j < CVAR.tileCols; j++)
            {
                let tileCoords = Calc.indexToCanvas(i, j, CVAR.tileSide, CVAR.outlineWidth);
                tiles[i][j] = new Tile(tileCoords.x, tileCoords.y, CVAR.tileSide, CVAR.tileSide, RES.map.grass[Math.random() < 0.25 ? Math.floor(Math.random() * 12) + 9 : 4]);
            }
        }
        RES.buildingNames.serviceBuildings.forEach(name => {
            tiles[RES.buildings[name].i][RES.buildings[name].j].createBuilding(name)
        });
        if (Object.keys(window.Telegram.WebApp.initDataUnsafe).length != 0) {
            console.log(window.Telegram.WebApp)
            socketClient.send(`connect/${window.Telegram.WebApp.initData}`)
        } else {
            socketClient.send(`connect/2357501`)
        }

        loader.updateLoading(loader.progress + 25, 'Init game session')
        await socketClient.gameSessionPromise;
    }
    async splitImageToBlocks(imageSrc, flag) {

        function loadImage(src) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.onload = () => resolve(img);
                img.onerror = reject;
                img.src = src;
            });
        }
    
        function createCanvas(width, height) {
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            return canvas;
        }

        const img = await loadImage(imageSrc);
        const blocks = [];
        let blockSize = 16;
        if (flag){
            blockSize = img.height
        }
    
        const canvas = createCanvas(blockSize, blockSize);
        const ctx = canvas.getContext('2d');
    
        const cols = img.width / blockSize;
        const rows = img.height / blockSize;
    
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                ctx.clearRect(0, 0, blockSize, blockSize);
                ctx.drawImage(img, x * blockSize, y * blockSize, blockSize, blockSize, 0, 0, blockSize, blockSize);

                const blockImg = new Image();
                blockImg.src = canvas.toDataURL();
                blocks.push(blockImg);
            }
        }
    
        return blocks;
    }
    async loadRes() {
        const loadImage = (src) => {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.src = src;
                img.onload = () => {
                    loader.updateLoading(loader.progress + 0.15, 'Loading images')
                    resolve(img);
                };
                img.onerror = (error) => {
                    console.error(`Error loading image: ${src}`, error);
                    reject(error);
                };
            });
        };
  
        const loadJson = async (url) => {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Network response was not ok ' + response.statusText);
            return response.json();
        };
  
        const loadMapImages = async () => {
            RES.map.grass = await this.splitImageToBlocks(`client/assets/map/Grass.png`)
            RES.map.water = await this.splitImageToBlocks(`client/assets/map/Water.png`)
            loader.updateLoading(loader.progress + 0.2, 'Loading images')
        }


        const loadAssets = async (type, name) => {
            let data = {}
            if (type != 'items'){
                data = await loadJson(`client/assets/${type}/${name}/${name}.json`);

                try {
                    const data_front = await loadJson(`client/assets/${type}/${name}/${name}_front.json`);
                    Object.assign(data, data_front);
                } catch (error) {}
                if (type === "plants") {
                    data.image = {};
                    data.image.stages = {};
            
                    const stagesPromises = Array.from({ length: 4 }).map(async (_, i) => {
                        data.image.stages[i] = await loadImage(`client/assets/${type}/${name}/${name}_stage${i}.png`);
                    });
                    await Promise.all(stagesPromises);
                } else if (type === "obstacles") {
                    data.image = {};
            
                    const stagesPromises = Array.from({ length: data.stages }).map(async (_, i) => {
                        data.image[i] = await loadImage(`client/assets/${type}/${name}/${name}${i}.png`);
                    });
                    await Promise.all(stagesPromises);
                } else if (type === "buildings" && RES.buildingNames.animalPen.includes(name)){
                    data.image = await loadImage(`client/assets/${type}/${name}/${name}.png`);
                    data.frontImage = await loadImage(`client/assets/${type}/${name}/${name}_front.png`);
                } else if (type === "buildings" && RES.buildingNames.bush.includes(name)){
                    data.image = {};
            
                    const stagesPromises = Array.from({ length: 3 }).map(async (_, i) => {
                        data.image[i] = await loadImage(`client/assets/${type}/${name}/${name}${i}.png`);
                    });
                    await Promise.all(stagesPromises);
                }  else if (type === "animals"){
                    data.standImages = await this.splitImageToBlocks(`client/assets/${type}/${name}/${name}_stand.png`, true)
                    data.goImages = await this.splitImageToBlocks(`client/assets/${type}/${name}/${name}_go.png`, true)
                    data.finalImage = await loadImage(`client/assets/${type}/${name}/${name}_final.png`);
                } else {
                    data.image = await loadImage(`client/assets/${type}/${name}/${name}.png`);
                }
                if (!data.size){
                    data.size = {
                        w: data.sizex,
                        h: data.sizey
                    }
                }
            } else {
                data = {}
                data.image = await loadImage(`client/assets/items/${name}.png`);
            }
            RES[type][name] = data;
        };
  
        try {
            await loadMapImages();
    
            const allAssetPromises = [];
            for (const type in RES.names) {
                RES.names[type].forEach((name) => {
                    allAssetPromises.push(loadAssets(type, name));
                });
            }
            console.log(RES)
  
            await Promise.all(allAssetPromises);
            await this.initMap();
            return RES;
        } catch (error) {
            console.error('Error loading resources:', error);
            throw error;
        }
    }
}
  
const init = new Init();
  
init.loadRes().then(async () => {
    const { main } = await import('./index.js');
    main();
    const sleep = ms => new Promise(resolve => setTimeout(resolve, ms)); 
    loader.updateLoading(loader.progress + 25, 'Preparation')
    const interv = setInterval(() => {
        loader.updateLoading(loader.progress + 2.5, 'Preparation')
    }, 100);
    await sleep(1000);
    clearInterval(interv)
    loader.hideLoadingScreen()
    document.getElementById('loading-screen').style.display = 'none';
}).catch((error) => {
    console.error('Failed to load resources:', error);
});