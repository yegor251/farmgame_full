class ConstVar{
    constructor() {
        this.tileSide = 10; this.outlineWidth = 0;
        this.tileRows = 20; this.tileCols = 20;
        this.minScale = 5 * window.innerHeight / 1000; this.maxScale = 15 * window.innerHeight / 1000;
        this.itemMapSize = 8; this.extraSlotsCount = 3;
        this.nextGardenPriceCoef = 1.2; this.nextBuildingPriceCoef = 100;
        this.animalPenCoef = 1.1;
        this.extraSlotPrice = 1000; this.extraSlotCoef = 10;
        this.orderCompleteTime = 60; this.orderRerollTime = 60;
        this.maxInvSize = 2000;
        this.redColor = 230; this.greenColor = 230;
        this.wallet = 'UQCF2EoQze-_Devg8oogD1KDNA-AdQCEpNnDFq5HIQLa6ZJh';
        this.transactionFee = 100000000
        this.spinTime = 28800
    }
}

const CVAR = new ConstVar();

export default CVAR;