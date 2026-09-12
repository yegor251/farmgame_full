document.getElementById('upgrade-stash-button').addEventListener('touchstart', () => {
    document.getElementById('upgrade-stash-button').style.backgroundImage = `url('client/assets/design/stash_button_upgrade_pressed.png')`
});

document.getElementById('upgrade-stash-button').addEventListener('touchend', () => {
    document.getElementById('upgrade-stash-button').style.backgroundImage = "url('client/assets/design/stash_button_upgrade.png')";
});

document.getElementById('closeStash').addEventListener('touchstart', () => {
    document.getElementById('closeStash').style.backgroundImage = `url('client/assets/design/button_exit_pressed.png')`
});

document.getElementById('closeStash').addEventListener('touchend', () => {
    document.getElementById('closeStash').style.backgroundImage = "url('client/assets/design/button_exit.png')";
});

document.getElementById('closeOrders').addEventListener('touchstart', () => {
    document.getElementById('closeOrders').style.backgroundImage = `url('client/assets/design/button_exit_pressed.png')`
});

document.getElementById('closeOrders').addEventListener('touchend', () => {
    document.getElementById('closeOrders').style.backgroundImage = "url('client/assets/design/button_exit.png')";
});

document.querySelectorAll('.buildable-close-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        button.style.backgroundImage = `url('client/assets/design/button_exit_pressed.png')`;
    });

    button.addEventListener('touchend', () => {
        button.style.backgroundImage = "url('client/assets/design/button_exit.png')";
    });
});

document.querySelectorAll('.buildable-close-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        button.style.backgroundImage = `url('client/assets/design/button_exit_pressed.png')`;
    });

    button.addEventListener('touchend', () => {
        button.style.backgroundImage = "url('client/assets/design/button_exit.png')";
    });
});

document.querySelectorAll('.exit_button_metal').forEach(button => {
    button.addEventListener('touchstart', () => {
        button.style.backgroundImage = `url('client/assets/design/exit_button_metal_2.png')`;
    });

    button.addEventListener('touchend', () => {
        button.style.backgroundImage = "url('client/assets/design/exit_button_metal_1.png')";
    });
});

document.querySelectorAll('.main-menu-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        let backgroundImage = getComputedStyle(button).backgroundImage;
        if (backgroundImage.includes('url(')) {
            let imagePath = backgroundImage.slice(5, -2);
            let newImagePath = imagePath.slice(0, -5) + '2.png';
            button.style.backgroundImage = `url('${newImagePath}')`;
        }
    });

    button.addEventListener('touchend', () => {
        let backgroundImage = getComputedStyle(button).backgroundImage;
        if (backgroundImage.includes('url(')) {
            let imagePath = backgroundImage.slice(5, -2);
            let newImagePath = imagePath.slice(0, -5) + '1.png';
            button.style.backgroundImage = `url('${newImagePath}')`;
        }
    });
});

document.getElementById('close-main-menu').addEventListener('touchstart', () => {
    document.getElementById('close-main-menu').style.backgroundImage = `url('client/assets/design/exit_main_button_2.png')`
});

document.getElementById('close-main-menu').addEventListener('touchend', () => {
    document.getElementById('close-main-menu').style.backgroundImage = "url('client/assets/design/exit_main_button_1.png')";
});

document.getElementById('networth-question-button').addEventListener('touchstart', () => {
    document.getElementById('networth-question-button').style.backgroundImage = `url('client/assets/design/question_button_2.png')`
});

document.getElementById('networth-question-button').addEventListener('touchend', () => {
    document.getElementById('networth-question-button').style.backgroundImage = "url('client/assets/design/question_button_1.png')";
});

document.getElementById('token-withdraw-button').addEventListener('touchstart', () => {
    document.getElementById('token-withdraw-button').style.backgroundImage = `url('client/assets/design/withdraw_butt_2.png')`
});

document.getElementById('token-withdraw-button').addEventListener('touchend', () => {
    document.getElementById('token-withdraw-button').style.backgroundImage = "url('client/assets/design/withdraw_butt_1.png')";
});

document.getElementById('confirm-withdraw').addEventListener('touchstart', () => {
    document.getElementById('confirm-withdraw').style.backgroundImage = `url('client/assets/design/grey_button_2.png')`
});

document.getElementById('confirm-withdraw').addEventListener('touchend', () => {
    document.getElementById('confirm-withdraw').style.backgroundImage = "url('client/assets/design/grey_button_1.png')";
});

document.getElementById('proceed-to-buy').addEventListener('touchstart', () => {
    document.getElementById('proceed-to-buy').style.backgroundImage = `url('client/assets/design/grey_button_2.png')`
});

document.getElementById('proceed-to-buy').addEventListener('touchend', () => {
    document.getElementById('proceed-to-buy').style.backgroundImage = "url('client/assets/design/grey_button_1.png')";
});

document.getElementById('referral-button').addEventListener('touchstart', () => {
    document.getElementById('referral-button').style.backgroundImage = `url('client/assets/design/referral_button_2.png')`
});

document.getElementById('referral-button').addEventListener('touchend', () => {
    document.getElementById('referral-button').style.backgroundImage = "url('client/assets/design/referral_button_1.png')";
});

document.getElementById('close-deals').addEventListener('touchstart', () => {
    document.getElementById('close-deals').style.backgroundImage = `url('client/assets/design/deal_exit_button2.png')`
});

document.getElementById('close-deals').addEventListener('touchend', () => {
    document.getElementById('close-deals').style.backgroundImage = "url('client/assets/design/deal_exit_button1.png')";
});

document.querySelectorAll('.upgrade-buildable-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        button.style.backgroundImage = "url('client/assets/design/stash_button_upgrade_pressed.png')";
    });

    button.addEventListener('touchend', () => {
        button.style.backgroundImage = "url('client/assets/design/stash_button_upgrade.png')";
    });
});

document.querySelectorAll('.claim-deposit-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        button.style.backgroundImage = "url('client/assets/design/grey_button_2.png')";
    });

    button.addEventListener('touchend', () => {
        button.style.backgroundImage = "url('client/assets/design/grey_button_1.png')";
    });
});

document.querySelectorAll('.donate-plus-button').forEach(button => {
    button.addEventListener('touchstart', () => {
        let backgroundImage = getComputedStyle(button).backgroundImage;
        if (backgroundImage.includes('url(')) {
            let imagePath = backgroundImage.slice(5, -2);
            let newImagePath = imagePath.slice(0, -5) + '2.png';
            button.style.backgroundImage = `url('${newImagePath}')`;
        }
    });

    button.addEventListener('touchend', () => {
        let backgroundImage = getComputedStyle(button).backgroundImage;
        if (backgroundImage.includes('url(')) {
            let imagePath = backgroundImage.slice(5, -2);
            let newImagePath = imagePath.slice(0, -5) + '1.png';
            button.style.backgroundImage = `url('${newImagePath}')`;
        }
    });
});

document.getElementById('ton-amount').addEventListener('keydown', function (e) {
    const allowedKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'Backspace'];
    if (!allowedKeys.includes(e.key)) {
        e.preventDefault();
    }

    const value = e.target.value;

    if (e.key === '.' && (value.includes('.') || value.length === 0)) {
        e.preventDefault();
        return;
    }
    if (e.key === 'Backspace' && value.includes('.')) {
        const parts = value.split('.');
        const dotIndex = value.indexOf('.') + 1;
        if (e.target.selectionStart === dotIndex) {
            e.target.value = parts[0];
            e.preventDefault();
        }
    }
});

document.getElementById('ton-amount').addEventListener('input', function (e) {
    let value = e.target.value;

    const parts = value.split('.');
    if (parts[0].length > 4) {
        e.target.value = value.slice(0, value.length - 1);
        return;
    }

    if (parts.length > 1 && parts[1].length > 6) {
        e.target.value = value.slice(0, value.length - 1);
    } else {
        e.target.value = value;
    }  
});

document.getElementById('ton-amount').addEventListener('paste', function (e) {
    e.preventDefault();
});

document.getElementById('withdraw-amount').addEventListener('keydown', function (e) {
    const allowedKeys = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 'Backspace'];
    if (!allowedKeys.includes(e.key)) {
        e.preventDefault();
    }

    const value = e.target.value;

    if (e.key === '.' && (value.includes('.') || value.length === 0)) {
        e.preventDefault();
        return;
    }
    if (e.key === 'Backspace' && value.includes('.')) {
        const parts = value.split('.');
        const dotIndex = value.indexOf('.') + 1;
        if (e.target.selectionStart === dotIndex) {
            e.target.value = parts[0];
            e.preventDefault();
        }
    }
});

document.getElementById('withdraw-amount').addEventListener('input', function (e) {
    let value = e.target.value;

    const parts = value.split('.');
    if (parts[0].length > 4) {
        e.target.value = value.slice(0, value.length - 1);
        return;
    }

    if (parts.length > 1 && parts[1].length > 2) {
        e.target.value = value.slice(0, value.length - 1);
    } else {
        e.target.value = value;
    }  
});

document.getElementById('withdraw-amount').addEventListener('paste', function (e) {
    e.preventDefault();
});

document.getElementById('selection-no').onclick = () => {
    document.getElementById('selection-menu-wrap').style.display = 'none'
}

document.getElementById("selection-menu-wrap").onclick = (e) => {
    if (e.target == document.getElementById("selection-menu-wrap"))
        document.getElementById('selection-menu-wrap').style.display = 'none'
};