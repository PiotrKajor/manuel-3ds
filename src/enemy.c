/* Menuel - enemies and projectiles */
#include "core.h"

/* art order: MITE MOTH FROG BELLFISH BEETLE FURNACE WRAITH HARE */
static const uint8_t en_hp[8] = { 2, 2, 3, 3, 4, 4, 4, 3 };
enum { BH_CRAWL, BH_FLY, BH_HOP, BH_SPIT };
static const uint8_t en_beh[8] = { BH_CRAWL, BH_FLY, BH_HOP, BH_SPIT, BH_CRAWL, BH_SPIT, BH_FLY, BH_HOP };

static const int8_t bob_tab[16] = { 0, 2, 4, 6, 6, 8, 8, 8, 8, 8, 6, 6, 4, 2, 0, 0 };

void spawn_enemy(uint8_t kind, int tx, int ty) {
    int i;
    for (i = 0; i < MAX_EN; i++)
        if (!G.en[i].on) {
            Enemy *e = &G.en[i];
            memset(e, 0, sizeof(*e));
            e->on = 1;
            e->kind = kind;
            e->hp = en_hp[kind];
            e->x = (int32_t)(tx * TS - 8) * (1 << FP);
            e->y = (int32_t)(ty * TS - 16) * (1 << FP);
            e->oy = e->y;
            e->dir = (uint8_t)(tx & 1);
            e->timer = (uint8_t)(tx * 7);
            return;
        }
}

void enemy_hit(Enemy *e, int dmg) {
    e->hp = e->hp > dmg ? (uint8_t)(e->hp - dmg) : 0;
    e->flash = 8;
    e->vx = G.p.face ? -700 : 700;
    e->state |= 0x80;
    sfx(SFX_HIT);
    part_spawn(0, PX(e->x) + 16, PX(e->y) + 16, 0, 0, 12);
    if (G.p.echo < 99) { G.p.echo = G.p.echo > 88 ? 99 : G.p.echo + 11; G.bot_dirty = 1; }
    G.hitstop = 3;
    if (!e->hp) {
        kill_fx(PX(e->x) + 16, PX(e->y) + 16);
        e->on = 0;
        G.counters[1]++;
    }
}

static void update_one(Enemy *e) {
    int ex = PX(e->x), ey = PX(e->y);
    int pcx = PX(G.p.x) + 16, pcy = PX(G.p.y) + 16;
    int dx = pcx - (ex + 16), dy = pcy - (ey + 16);
    uint8_t beh = en_beh[e->kind];
    if (e->flash) e->flash--;
    if (e->state & 0x80) {
        /* knockback */
        int nx = PX(e->x + e->vx);
        if (!box_solid(nx + 4, ey + 8, 24, 20)) e->x += e->vx;
        e->vx = e->vx * 3 / 4;
        if (e->vx > -80 && e->vx < 80) { e->vx = 0; e->state &= 0x7F; }
        if (beh == BH_HOP) { e->vy = 0; }
    } else switch (beh) {
    case BH_CRAWL: {
        int speed = e->kind == 4 ? 180 : 110;
        int fx = e->dir ? ex + 30 : ex + 1;
        if (solid_at(fx, ey + 20)) e->dir ^= 1;
        else {
            uint8_t below = cell(fx >> 4, (ey + 32) >> 4);
            if (below != T_ROCK && below != T_ONEWAY && below != T_CRACK && below != T_DOOR) e->dir ^= 1;
        }
        e->x += e->dir ? speed : -speed;
        break;
    }
    case BH_FLY: {
        int acc = e->kind == 6 ? 18 : 12, lim = e->kind == 6 ? 300 : 210;
        if (e->state == 0) {
            e->y = e->oy + ((int32_t)bob_tab[(G.frame >> 3) & 15] << FP);
            if (dx < 110 && dx > -110 && dy < 90 && dy > -90) e->state = 1;
        } else {
            e->vx += dx > 0 ? acc : -acc;
            e->vy += dy > 0 ? acc : -acc;
            if (e->vx > lim) e->vx = lim;
            if (e->vx < -lim) e->vx = -lim;
            if (e->vy > lim) e->vy = lim;
            if (e->vy < -lim) e->vy = -lim;
            if (!box_solid(PX(e->x + e->vx) + 6, ey + 6, 20, 20)) e->x += e->vx; else e->vx = 0;
            if (!box_solid(ex + 6, PX(e->y + e->vy) + 6, 20, 20)) e->y += e->vy; else e->vy = 0;
            e->oy = e->y;
            if (dx > 220 || dx < -220) e->state = 0;
        }
        e->dir = dx > 0;
        break;
    }
    case BH_HOP: {
        int grounded = box_solid(ex + 4, ey + 32, 24, 1) || cell((ex + 16) >> 4, (ey + 32) >> 4) == T_ONEWAY;
        if (grounded && e->vy >= 0) {
            e->vy = 0;
            e->y = (int32_t)(((ey + 32) >> 4) * TS - 32) << FP;
            e->vx = 0;
            if (e->timer) e->timer--;
            else {
                e->timer = 60;
                e->dir = dx > 0;
                e->vy = e->kind == 7 ? -1500 : -1250;
                e->vx = e->dir ? (e->kind == 7 ? 420 : 300) : (e->kind == 7 ? -420 : -300);
            }
        } else {
            e->vy += 90;
            if (e->vy > 1400) e->vy = 1400;
            if (box_solid(PX(e->x + e->vx) + 4, ey + 8, 24, 20)) e->vx = -e->vx;
            e->x += e->vx;
            if (e->vy < 0 && box_solid(ex + 4, PX(e->y + e->vy) + 4, 24, 4)) e->vy = 0;
            e->y += e->vy;
            ey = PX(e->y);
            if (e->vy > 0 && box_solid(ex + 4, ey + 32, 24, 1)) {
                e->y = (int32_t)(((ey + 32) >> 4) * TS - 32) << FP;
                e->vy = 0;
            }
            if (ey > SH + 16) e->on = 0;
        }
        break;
    }
    case BH_SPIT:
        e->dir = dx > 0;
        if (e->timer) e->timer--;
        else if (dx < 200 && dx > -200) {
            e->timer = 120;
            if (e->kind == 3) proj_spawn(P_DROP, ex + 12, ey + 28, 0, 200, 1);
            else proj_spawn(P_ORB, ex + 12, ey + 4, dx > 0 ? 500 : -500, -900, 1);
            sfx(SFX_SELECT);
        }
        break;
    }
    ex = PX(e->x); ey = PX(e->y);
    if (e->on && !G.p.hurt && !G.p.dead &&
        overlap(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH, ex + 4, ey + 8, 24, 22))
        player_hurt(1, pcx < ex + 16 ? -1 : 1);
}

void enemy_update(void) {
    int i;
    for (i = 0; i < MAX_EN; i++)
        if (G.en[i].on) update_one(&G.en[i]);
}

void proj_spawn(uint8_t kind, int x, int y, int vx, int vy, uint8_t grav) {
    int i;
    for (i = 0; i < MAX_PROJ; i++)
        if (!G.pr[i].on) {
            Proj *q = &G.pr[i];
            q->on = 1; q->kind = kind; q->grav = grav;
            q->x = (int32_t)x * (1 << FP); q->y = (int32_t)y * (1 << FP); q->vx = vx; q->vy = vy;
            return;
        }
}

void proj_update(void) {
    int i;
    for (i = 0; i < MAX_PROJ; i++) {
        Proj *q = &G.pr[i];
        int x, y;
        if (!q->on) continue;
        q->x += q->vx;
        q->y += q->vy;
        if (q->grav) q->vy += 60;
        x = PX(q->x); y = PX(q->y);
        if (x < -16 || x > SW + 16 || y > SH + 16 || y < -40) { q->on = 0; continue; }
        if (q->kind == P_WAVE) {
            if (solid_at(q->vx > 0 ? x + 16 : x, y + 16)) { q->on = 0; continue; }
        } else if (y > 0 && solid_at(x + 8, y + 24)) {
            part_spawn(0, x + 8, y + 20, 0, 0, 10);
            q->on = 0;
            continue;
        }
        if (!G.p.hurt && !G.p.dead &&
            overlap(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH, x + 3, y + 6, 10, 22))
            player_hurt(1, q->vx > 0 ? 1 : -1);
    }
}
