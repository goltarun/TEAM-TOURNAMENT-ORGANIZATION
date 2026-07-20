(function () {
    function ready(fn) {
        if (document.readyState !== 'loading') {
            fn();
            return;
        }
        document.addEventListener('DOMContentLoaded', fn);
    }

    ready(function () {
        var gameMode = document.getElementById('id_game_mode');
        var teamMode = document.getElementById('id_mode');
        var slots = document.getElementById('id_max_slots');

        if (!gameMode || !teamMode || !slots) {
            return;
        }

        var slotRules = {
            'BR Rank': {
                Solo: 48,
                Duo: 24,
                Squad: 12
            },
            'Clash Squad': {
                Solo: 2,
                Duo: 2,
                Squad: 2
            }
        };

        function updateSlots() {
            var gameRules = slotRules[gameMode.value] || {};
            var slotCount = gameRules[teamMode.value];

            if (slotCount) {
                slots.value = slotCount;
            }
        }

        slots.readOnly = true;
        slots.title = 'Slots are set automatically from Game Mode and Team Mode.';

        gameMode.addEventListener('change', updateSlots);
        teamMode.addEventListener('change', updateSlots);
        updateSlots();
    });
}());
