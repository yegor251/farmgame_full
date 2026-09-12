import player from "../player/player.js";
import socketClient from "../../init.js";
import GVAR from "../../globalVars/global.js";

class TransactionsMenu {
    constructor() {
        document.getElementById("closeTransaction").onclick = () => this.close();
        document.getElementById('open-transactions').onclick = () => {
            GVAR.closeAllWindows();
            document.getElementById('transaction-wrap').style.display = 'flex'
            this.show();
        }
        document.getElementById("transaction-wrap").onclick = (e) => {
            if (e.target == document.getElementById("transaction-wrap"))
                this.close()
        };
    }
    show(){
        function formatTime(timeStamp) {
            const date = new Date(timeStamp * 1000);
            const options = {
                day: '2-digit',
                month: 'short',
                hour: '2-digit',
                minute: '2-digit'
            };
            return date.toLocaleString('en-GB', options).replace(', ', ',');
        }        

        const transactionsContent = document.getElementById('transactions-content');
        transactionsContent.innerHTML = ''
        const blockDiv = document.createElement('div');
        blockDiv.className = 'manual-pay'
        const transText = document.createElement('h3');
        blockDiv.appendChild(transText)
        transText.innerText = GVAR.localization[13][GVAR.language]
        transText.className = 'trans-text'
        transactionsContent.appendChild(blockDiv)
        if (player._transactions.length == 0){
            const blockDiv = document.createElement('div');
            blockDiv.className = 'manual-pay'
            const text = document.createElement('h3');
            text.innerText = GVAR.localization[14][GVAR.language]
            text.className = 'trans-empty-text'
            blockDiv.appendChild(text)
            transactionsContent.appendChild(blockDiv)
            return
        }

        const table = document.createElement('div');
        table.className = 'transactions-table'
        
        player._transactions.forEach(item => {
            const row = document.createElement('div');
            row.className = 'transactions-table-row'
        
            const timeCell = document.createElement('div');
            const timeCelltext = document.createElement('h3');
            timeCelltext.className = 'table-text'
            timeCelltext.innerText = formatTime(item.time_stamp);

            timeCell.className = 'table-col1';
            timeCell.appendChild(timeCelltext)
            row.appendChild(timeCell);
        
            const typeCell = document.createElement('div');
            const arrow = document.createElement('div');
            arrow.className = item.type === 'dep' ? 'deposit-arrow' : 'withdraw-arrow';

            typeCell.className = 'table-col2';
            typeCell.appendChild(arrow)
            row.appendChild(typeCell);
        
            const walletCell = document.createElement('div');
            const walletCelltext = document.createElement('h3');
            walletCelltext.className = 'table-text'
            walletCelltext.innerText = item.type === 'dep' ? '-' : `${item.wallet.slice(0, 3)}..${item.wallet.slice(-3)}`;

            walletCell.className = 'table-col3';
            walletCell.appendChild(walletCelltext)
            row.appendChild(walletCell);
        
            const jettonSignatureCell = document.createElement('div');
            const jettonSignatureCelltext = document.createElement('h3');
            jettonSignatureCelltext.className = 'table-text'
            jettonSignatureCelltext.innerText = item.jetton_signature;

            jettonSignatureCell.className = 'table-col4';
            jettonSignatureCell.appendChild(jettonSignatureCelltext)
            row.appendChild(jettonSignatureCell);
        
            const amountCell = document.createElement('div');
            const amountCelltext = document.createElement('h3');
            amountCelltext.className = 'table-text'
            if (item.type === 'dep'){
                if (item.jetton_signature === "TON")
                    amountCelltext.innerText = '+' + (item.amount / 1000000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0]
                else if (item.jetton_signature === "USDT")
                    amountCelltext.innerText = '+' + (item.amount / 1000000).toString().match(/^-?\d+(?:\.\d{0,3})?/)[0]
                else
                    amountCelltext.innerText = '+' + (item.amount / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0]
                amountCelltext.classList.add('unlocked')
            } else {
                amountCelltext.innerText = '-' + (item.amount / 100).toString().match(/^-?\d+(?:\.\d{0,2})?/)[0]
                amountCelltext.classList.add('locked')
            }
            amountCell.className = 'table-col5';
            amountCell.appendChild(amountCelltext)
            row.appendChild(amountCell);
        
            const claimCell = document.createElement('div');
            claimCell.className = 'table-col6';
            const claimButton = document.createElement('div');
            if (item.type === 'dep' && item.active){
                claimButton.className = 'claim-deposit-button'
                const claimText = document.createElement('h3');
                claimText.className = 'claim-deposit-text'
                claimText.classList.add('unlocked')
                claimText.innerText = GVAR.localization[12][GVAR.language]
                claimButton.appendChild(claimText);
                claimButton.onclick = () => {
                    socketClient.send(`claim/${item.index}`);
                    socketClient.send('regen')
                    item.active = false;
                    this.show();
                }
            } else {
                claimButton.className = 'img-claimed';
            }
            claimCell.appendChild(claimButton);
            row.appendChild(claimCell);
        
            table.appendChild(row);
        });
          
        transactionsContent.appendChild(table);                 
    }
    close() {
        document.getElementById('transaction-wrap').style.display = 'none';
        document.getElementById("main-menu-wrap").style.display = "flex";
    }
}

export const transactionsMenu = new TransactionsMenu();