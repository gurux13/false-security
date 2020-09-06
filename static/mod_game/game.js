Vue.component('player-icon', {
    props: [
        'name',
        'score',
        'divclass'
    ],
    template: `
    <div class="player-icon" v-bind:class="divclass">
    Игрок...
        <div class="player-name">
            {{name}}
        </div>
        <div class="player-score">
            {{score}}
        </div>
    </div>
    `,
});

Vue.component('card', {
    props: [
        'cards',
        'card_id',
        'type',
        'cls',
    ],
    data: function() {
        let type_cls = "";
        switch (this.type) {
            case 'off':
                type_cls = 'card_offence';
                break;
            case 'acc':
                type_cls = 'card_accident';
                break;
            case 'def':
                type_cls = 'card_defence';
                break;
        }
        return {
            css_cls: type_cls + ' ' + this.cls + ' card'
        }
    },
    computed: {
        card: function () {
            console.log("MASTER CARD", this.card_id);
            return this.cards[this.card_id];
        },

    },
    methods: {
        get_card: function(card_id) {
            console.log("GET CARD", card_id);
            return this.cards[card_id];
        }
    },
    template: `
    <div :class="css_cls">
        <p>
            <b>{{card.name}}</b>
            {{card.damage}}&nbsp;<span class="falsic"></span></p>
        <div v-if="card.off_against">
            <div class="against" v-for="elem in card.off_against" :key="elem.id">
                {{get_card(elem.other_card).name}} -{{elem.value}}<br/>
            </div>
        </div>
    </div>
`
});


