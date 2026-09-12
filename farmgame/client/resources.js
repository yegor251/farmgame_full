class Resources {
  constructor() {
    this.plants = {};
    this.buildings = {};
    this.items = {};
    this.animals = {};
    this.obstacles = {};
    this.map = {};
    this.names = {};
    this.buildingNames = {}
    this.names.buildings = [];
    this.buildingNames.bakery = ["bakery", 'crusher', 'dairy', 'sugar_factory', 'popcorn_maker', 'grill', 'oven', 'loom', 'juicer']
    this.buildingNames.garden = ["garden"]
    this.buildingNames.animalPen = ['coop', 'cowshed', 'pigsty', 'sheepfold']
    this.buildingNames.bush = ['apple_tree', 'raspberry', 'cherry', 'blackberry', 'strawberry']
    this.buildingNames.serviceBuildings = ['barn', 'spin_wheel', 'orders_board'];
    for (const type in this.buildingNames) {
      this.buildingNames[type].forEach(name => {
        this.names.buildings.push(name)
      });
    }
    this.names.plants = ["wheat", "corn", 'soy', 'sugarCane', 'carrot', 'pumpkin', 'indigo', 'pepper', 'tomato', 'cotton', 'potato'];
    this.names.items = ['bread', 'cornbread', 'chickenFeed', 'cowFeed', 'pigFeed', 'sheepFeed',
      'cream', 'butter', 'cheese', 'brownSugar', 'whiteSugar', 'syrup', 
      'cookie', 'pancakes', 'popcorn', 'butterPopcorn', 'chilePopcorn', 'sweetPopcorn', 
      'omelet', 'hamburger', 'bakedTomato', 'blackberryCupcake', 'raspberryCupcake', 
      'carrotPie', 'pumpkinPie', 'applePie', 'baconPie', 'carrotCake', 'creamCake',
      'sweater', 'cottonFabric', 'blueCap', 'shirt', 'cherryPie', 'cheesecake', 'strawberryCake',
      'pizza', 'spicyPizza', 'blueSweater', 'shorts', 'purpleDress', 'redScarf', 
      'potatoBread', 'bakedPotato', 'carrotJuice', 'appleJuice', 'cherryJuice', 'tomatoJuice', 'berryJuice']; //только крафты
    this.names.animals = ['chicken', 'cow', 'pig', 'sheep'];
    this.names.obstacles = ["small_swamp", 'medium_swamp', 'huge_swamp', 'stone_big', 'autumn_big_tree', 'autumn_tight_tree', 'autumn_tree', 'autumn_tree_fall', 'tree', 'big_stump', 'log', 'small_stump', 'stone_small', 'tree_big', 'tree_fall'];
    this.mapImgNames = ["grass_1", "grass_2"];
  }
}

const RES = new Resources();

export default RES;

