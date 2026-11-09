#include "gesture.h"
static bool debounce(cap_button *b, bool raw, uint32_t ms) {
    if (raw != b->candidate) { b->candidate = raw; b->since = ms; }
    if (b->stable != raw && (uint32_t)(ms - b->since) >= 30) {
        b->stable = raw; return true;
    }
    return false;
}
void cap_step(cap_gesture *g, uint32_t ms, bool b1, bool b2, int pos,
              cap_emit emit, void *u) {
    bool e1 = debounce(&g->b[0], b1, ms);
    bool e2 = debounce(&g->b[1], b2, ms);
    /* One toggle per debounced B1 rising edge. Holding never repeats. */
    if (e1 && g->b[0].stable) {
        g->vertical = !g->vertical;
        emit("MODE", 0, g->vertical?'Y':'X', u);
    }
    char mode = g->vertical ? 'Y' : 'X';
    if (e1) emit("BUTTON1", g->b[0].stable, mode, u);
    if (e2) {
        emit("BUTTON2", g->b[1].stable, mode, u);
        emit("LEFT_CLICK", g->b[1].stable, mode, u);
    }
    if (pos >= 0 && pos <= 100) {
        if ((!g->slider || pos != g->position || mode != g->last_mode) &&
            (!g->slider || mode != g->last_mode || (uint32_t)(ms-g->last_move)>=20)) {
            emit("MOVE", pos, mode, u); g->position=pos;
            g->last_move=ms; g->last_mode=mode;
        }
        g->slider=true;
    } else if (g->slider) {
        g->slider=false; emit("RELEASE", 0, mode, u);
    }
}
