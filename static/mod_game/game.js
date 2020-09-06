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
        'cls',
        'tiny',
        'vs',
    ],
    computed: {
        card: function () {
            return this.cards[this.card_id];
        },
        def_value: function () {
            console.log("DEF AGAINST", this.card.def_against);
            return this.card.def_against.filter((x) => x.other_card == this.vs)[0].value;
        },
        dmg_value: function () {
            if (this.type == 'def') {
                return this.def_value;
            }
            return this.card.damage;
        },
        css_cls: function () {
            let type_cls = "";
            const thecard = this.cards[this.card_id];
            console.log("My card:", thecard);
            switch (thecard.type) {
                case 1:
                    type_cls = 'card_offence';
                    break;
                case 2:
                    type_cls = 'card_accident';
                    break;
                case 0:
                    type_cls = 'card_defence';
                    break;
            }
            return type_cls + ' ' + this.cls + ' card'
        }
    },
    methods: {
        get_card: function (card_id) {
            console.log("GET CARD", card_id);
            return this.cards[card_id];
        }
    },
    template: `
    <div :class="css_cls">
        <div class="card_falsics">
            {{dmg_value}}<span class="falsic"></span>
        </div>
        <p>
            <b>{{card.name}}</b>
        </p>
        <div v-if="card.off_against">
            <div class="against" v-for="elem in card.off_against" :key="elem.id">
                {{get_card(elem.other_card).name}} -{{elem.value}}<br/>
            </div>
        </div>
        <div v-if="card.def_against && !tiny">
            <div class="against" v-for="elem in card.def_against" :key="elem.id">
                {{get_card(elem.other_card).name}} +{{elem.value}}<br/>
            </div>
        </div>     
<!--        <div v-if="vs && tiny">-->
<!--            <div class="against" >-->
<!--                {{get_card(vs).name}} +{{def_value}}<br/>-->
<!--            </div>-->
<!--        </div>             -->
    </div>
`
});


