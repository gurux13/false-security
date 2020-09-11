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
            const def = this.card.def_against.filter((x) => x.other_card == this.vs)[0];
            return (def && def.value) || 0;
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
        is_def: function () {
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
            return type_cls + ' ' + this.cls + ' card';
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
        },
        clicked_big: function () {
            if (this.card.type == -1) {
                this.clicked();
            }
        },
        popup: function () {
            cardBig.show(this.card.id);
        }
    },
    template: `
    <div :class="css_cls" @click="clicked_big">
        <div v-if="card.type != -1" class="card_more_wrapper">
            <div class="card_more" @click="popup">
                Подробнее
            </div>
            <div class="card_more card_play" @click="clicked" v-if="can_play">
                Сыграть карту
            </div>            
        </div>
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

const full_cards = {};

Vue.component('cardbig', {
    data: function () {
        return {
            name: "",
            loaded: false,
            id: -1,
            text: "",
            url: "",
            shown: false,
            subscribed: false
        };
    },
    template: `
        <div v-if="shown" class="cardbig">
            <div class="overlay" @click="hide"></div>
            <div v-if="loaded" :class="css_cls">
                <div class="card_name">
                    {{name}}
                </div>
                <p>
                {{text}}
                </p>
                <a v-if="url" :href="url">Глоссарий</a>
            </div>
        </div>
        
    `,
    mounted: function() {
        const self = this;
        socket.on('card', (data) => {
            full_cards[data.value.id] = data.value;
            self.onload();
        });
    },
    computed: {
        card: function() {
            return full_cards[this.id];
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
            return type_cls + ' cardbig-content';
        }
    },
    methods: {
        onload: function() {
            if (full_cards[this.id]) {
                const card = full_cards[this.id];
                this.name = card.name;
                this.text = card.pop_up_text;
                this.url = card.pop_up_url;
                this.loaded = true;
            }
        },
        show: function (id) {
            if (!this.subscribed) {
                const self = this;

            }
            this.loaded = false;
            this.id = id;
            this.shown = true;
            socket.emit('card', id);
        },
        hide: function () {
            this.shown = false;
        }
    }
});

let cardBig = undefined;

Vue.mixin(
    {
        mounted: function () {
            if (this.$root === this) {
                var ne = document.createElement("div");
                ne.id = "placeholderGLOBAL";
                this.$el.appendChild(ne);
                var dp = Vue.component("cardbig");
                cardBig = new dp({parent: this, el: "#placeholderGLOBAL"});
                cardBig.$mount();
            }
        }
    });

