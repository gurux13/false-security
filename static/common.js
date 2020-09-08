function copyToClipboard(text) {
    input = document.createElement('input');
    input.value = text;
    document.body.appendChild(input);
    input.select();
    input.setSelectionRange(0, 9999);
    document.execCommand('copy');
    document.body.removeChild(input);
}

function snackbar(text) {
    // Get the snackbar DIV
    let x = document.getElementById("snackbar");
    x.className = x.className.replace("show", "");
    const key = Math.random();
    x.snack_id = key;

    setTimeout(function () {
        x.innerText = text;
        // Add the "show" class to DIV
        x.className = "show";
    }, 10);


    // After 3 seconds, remove the show class from DIV
    setTimeout(function () {
        if (x.snack_id == key) {
            x.className = x.className.replace("show", "");
        }
    }, 3000);
}

Vue.component('gamelink', {
        props: [
            'link',
            'display_link'
        ],
        template: `
    <a href="#" v-on:click="copyLink" title="Нажмите, чтобы скопировать ссылку">{{display_link}}</a>
    `,
        methods: {
            copyLink: function () {
                const full_link = window.location.href.replace(/\/[^\/]*$/, '').toString() + this.link;
                copyToClipboard(full_link);
                snackbar("Ссылка скопирована");
            }
        },
        name: 'gamelink',
    }
);