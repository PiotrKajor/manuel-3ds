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
            e->x = (int32_t)(tx * TS + 8 - EW / 2) * (1 << FP);
            e->y = (int32_t)((ty + 1) * TS - EH) * (1 << FP);
            e->oy = e->y;
            e->dir = (uint8_t)(tx & 1);
            e->timer = (uint8_t)(tx * 7);
            return;
        }
}

void enemy_hit(Enemy *e, int dmg) {
    e->hp = e->hp > dmg ? (uint8_t)(e->hp - dmg) : 0;
    e->flash = 8;
    e->vx = G.p.face ? -800 : 800;
    e->state |= 0x80;
    sfx(SFX_HIT);
    part_spawn(0, PX(e->x) + EW / 2, PX(e->y) + EH / 2, 0, 0, 12);
    if (G.p.echo < 99) G.p.echo = G.p.echo > 88 ? 99 : G.p.echo + 11;
    G.hitstop = 3;
    if (!e->hp) {
        kill_fx(PX(e->x) + EW / 2, PX(e->y) + EH / 2);
        e->on = 0;
        G.counters[1]++;
    }
}

static int standing(int ex, int ey) {
    uint8_t c = cell((ex + EW / 2) >> 4, (ey + EH) >> 4);
    return !((ey + EH) & 15) && (box_solid(ex + 8, ey + EH, EW - 16, 1) || c == T_ONEWAY);
}

static void update_one(Enemy *e) {
    int ex = PX(e->x), ey = PX(e->y);
    int pcx = PX(G.p.x) + PW / 2, pcy = PX(G.p.y) + PH / 2;
    int dx = pcx - (ex + EW / 2), dy = pcy - (ey + EH / 2);
    uint8_t beh = en_beh[e->kind];
    if (e->flash) e->flash--;
    if (e->state & 0x80) {
        int nx = PX(e->x + e->vx);
        if (!box_solid(nx + 8, ey + 10, EW - 16, EH - 14)) e->x += e->vx;
        e->vx = e->vx * 3 / 4;
        if (e->vx > -80 && e->vx < 80) { e->vx = 0; e->state &= 0x7F; }
        if (beh == BH_HOP) e->vy = 0;
    } else switch (beh) {
    case BH_CRAWL: {
        int speed = e->kind == 4 ? 220 : 130;
        int fx = e->dir ? ex + EW - 6 : ex + 6;
        if (solid_at(fx, ey + EH - 12)) e->dir ^= 1;
        else {
            uint8_t below = cell(fx >> 4, (ey + EH) >> 4);
            if (below != T_ROCK && below != T_ONEWAY && below != T_CRACK && below != T_DOOR) e->dir ^= 1;
        }
        e->x += e->dir ? speed : -speed;
        break;
    }
    case BH_FLY: {
        int acc = e->kind == 6 ? 18 : 12, lim = e->kind == 6 ? 320 : 230;
        if (e->state == 0) {
            e->y = e->oy + ((int32_t)bob_tab[(G.frame >> 3) & 15] * (1 << FP));
            if (dx < 130 && dx > -130 && dy < 110 && dy > -110) e->state = 1;
        } else {
            e->vx += dx > 0 ? acc : -acc;
            e->vy += dy > 0 ? acc : -acc;
            if (e->vx > lim) e->vx = lim;
            if (e->vx < -lim) e->vx = -lim;
            if (e->vy > lim) e->vy = lim;
            if (e->vy < -lim) e->vy = -lim;
            if (!box_solid(PX(e->x + e->vx) + 10, ey + 8, EW - 20, EH - 16)) e->x += e->vx; else e->vx = 0;
            if (!box_solid(ex + 10, PX(e->y + e->vy) + 8, EW - 20, EH - 16)) e->y += e->vy; else e->vy = 0;
            e->oy = e->y;
            if (dx > 260 || dx < -260) e->state = 0;
        }
        e->dir = dx > 0;
        break;
    }
    case BH_HOP:
        if (standing(ex, ey) && e->vy >= 0) {
            e->vy = 0;
            e->vx = 0;
            if (e->timer) e->timer--;
            else {
                e->timer = 60;
                e->dir = dx > 0;
                e->vy = e->kind == 7 ? -1700 : -1400;
                e->vx = e->dir ? (e->kind == 7 ? 460 : 340) : (e->kind == 7 ? -460 : -340);
                e->y += e->vy;
            }
        } else {
            int steps, sd;
            e->vy += 90;
            if (e->vy > 1500) e->vy = 1500;
            if (box_solid(PX(e->x + e->vx) + 8, ey + 10, EW - 16, EH - 14)) e->vx = -e->vx;
            e->x += e->vx;
            ex = PX(e->x);
            steps = PX(e->y + e->vy) - PX(e->y);
            sd = steps < 0 ? -1 : 1;
            while (steps) {
                int ny = PX(e->y) + sd;
                if (sd < 0 && box_solid(ex + 8, ny + 6, EW - 16, 4)) { e->vy = 0; break; }
                e->y += sd * (1 << FP);
                steps -= sd;
                if (sd > 0 && standing(ex, PX(e->y))) { e->vy = 0; break; }
            }
            if (PX(e->y) > WH + 16) e->on = 0;
        }
        break;
    case BH_SPIT:
        e->dir = dx > 0;
        if (e->timer) e->timer--;
        else if (dx < 220 && dx > -220 && dy > -220 && dy < 220) {
            e->timer = 120;
            if (e->kind == 3) proj_spawn(P_DROP, ex + EW / 2, ey + EH, 0, 200, 1);
            else proj_spawn(P_ORB, ex + EW / 2, ey + 8, dx > 0 ? 560 : -560, -1000, 1);
            sfx(SFX_SELECT);
        }
        break;
    }
    ex = PX(e->x); ey = PX(e->y);
    if (e->on && !G.p.hurt && !G.p.dead &&
        overlap(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH, ex + 8, ey + 10, EW - 16, EH - 12))
        player_hurt(1, pcx < ex + EW / 2 ? -1 : 1);
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
        if (x < -16 || x > WW + 16 || y > WH + 16 || y < -80) { q->on = 0; continue; }
        if (q->kind == P_WAVE) {
            if (solid_at(q->vx > 0 ? x + 12 : x - 12, y)) { q->on = 0; continue; }
        } else if (y > 0 && solid_at(x, y + 8)) {
            part_spawn(0, x, y, 0, 0, 10);
            q->on = 0;
            continue;
        }
        if (!G.p.hurt && !G.p.dead &&
            overlap(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH, x - 7, y - 9, 14, 20))
            player_hurt(1, q->vx > 0 ? 1 : -1);
    }
}
