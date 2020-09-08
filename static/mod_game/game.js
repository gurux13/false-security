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
        'can_play',
        'cur_damage',
    ],
    computed: {
        card: function () {
            if (this.card_id == -1) {
                return {
                    name: "Закончить и заплатить " + this.cur_damage + "<span class='falsic'>",
                    type: -1,
                };
            }
            return this.cards[this.card_id];
        },
        def_value: function () {
            if (!this.vs) {
                return 0;
            }
            return this.card.def_against.filter((x) => x.other_card == this.vs)[0].value;
        },
        dmg_value: function () {
            if (this.card.type == -1) {
                return 0;
            }
            if (this.card.type == 0) {
                return this.def_value;
            }
            return this.card.damage;
        },
        is_def: function() {
            return this.card.type == 0;
        },
        css_cls: function () {
            let type_cls = "";
            switch (this.card.type) {
                case 1:
                    type_cls = 'card_offence';
                    break;
                case 2:
                    type_cls = 'card_accident';
                    break;
                case 0:
                    type_cls = 'card_defence';
                    break;
                case -1:
                    type_cls = 'card_money';
            }
            return type_cls + ' ' + this.cls + ' card'
        }
    },
    methods: {
        get_card: function (card_id) {
            return this.cards[card_id];
        },
        clicked: function () {
            if (this.can_play) {
                this.$emit('clicked', this.card_id);
            }
        }
    },
    template: `
    <div :class="css_cls" @click="clicked">
        <div class="card_falsics" v-if="tiny || dmg_value">
            {{dmg_value}}<span class="falsic"></span>
        </div>
        <p>
            <b v-html="card.name"></b>
        </p>
        <div v-if="card.off_against">
            <div class="against" v-for="elem in card.off_against" :key="elem.id">
                {{get_card(elem.other_card).name}} -{{elem.value}}<br/>
            </div>
        </div>
        <div v-if="(card.def_against && !tiny)">
            <div class="against" v-for="elem in card.def_against" :key="elem.id">
                {{get_card(elem.other_card).name}} +{{elem.value}}<br/>
            </div>
        </div>     
    </div>
`
});


