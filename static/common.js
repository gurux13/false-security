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
    x.innerText = text;
    // Add the "show" class to DIV
    x.className = "show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function () {
        x.className = x.className.replace("show", "");
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
                copyToClipboard(this.link);
                snackbar("Ссылка скопирована");
            }
        },
        name: 'gamelink',
    }
);