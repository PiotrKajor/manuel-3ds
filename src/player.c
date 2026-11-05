/* Menuel - movement, abilities, interaction */
#include "core.h"

#define WALK_ACC 64
#define WALK_MAX 640
#define JUMP_V 1792
#define AIRJUMP_V 1600
#define JUMP_CUT 512
#define GRAV 90
#define FALL_MAX 1536
#define RUSH_V 1536
#define RUSH_T 12
#define HOOK_V 1536
#define HOOK_RANGE 136
#define CLEAVE_V 1792

void player_hurt(uint8_t amount, int dirx) {
    Player *p = &G.p;
    if (p->hurt || p->dead) return;
    G.counters[2]++;
    if (g_god) { p->hurt = 40; return; }
    p->hp = p->hp > amount ? p->hp - amount : 0;
    p->hurt = 80;
    p->stun = 14;
    p->heal = 0;
    p->dash = 0;
    p->atk = 0;
    p->hook = 0;
    p->cleave = 0;
    p->vx = dirx * 500;
    p->vy = -900;
    G.hitstop = 5;
    G.shake = 8;
    G.bot_dirty = 1;
    sfx(SFX_HURT);
    if (p->hp == 0) { p->dead = 1; sfx(SFX_DIE); }
}

static void hazard_reset(void) {
    Player *p = &G.p;
    player_hurt(1, 0);
    if (!p->dead) {
        p->x = p->safe_x; p->y = p->safe_y;
        p->vx = 0; p->vy = 0; p->dash = 0; p->hook = 0; p->cleave = 0;
    }
}

static int find_anchor(int dir) {
    const RoomDef *r = &rooms[G.room];
    int i, best = -1, pass;
    int pcx = PX(G.p.x) + 16, pcy = PX(G.p.y) + 16;
    /* first look only in the held direction, then anywhere; never the ring just used */
    for (pass = dir ? 0 : 1; pass < 2 && best < 0; pass++) {
        int32_t best_d = (int32_t)HOOK_RANGE * HOOK_RANGE;
        for (i = 0; i < r->nent; i++) {
            const Ent *e = &r->ent[i];
            if (e->type == ENT_ANCHOR && i != G.p.hook_last) {
                int32_t dx = e->tx * TS + 8 - pcx, dy = e->ty * TS + 8 - pcy;
                int32_t d = dx * dx + dy * dy;
                if (pass == 0 && (dir > 0 ? dx <= 0 : dx >= 0)) continue;
                if (d < best_d) { best_d = d; best = i; }
            }
        }
    }
    return best;
}

static void break_crack(void) {
    const RoomDef *r = &rooms[G.room];
    int i, x = PX(G.p.x) + HX, y = PX(G.p.y) + 32;
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        if (e->type == ENT_CRACK && !HAS(e->arg)) {
            int ex = e->tx * TS, ew = e->arg2 * TS, ey = e->ty * TS;
            if (x + HW > ex && x < ex + ew && y >= ey - 2 && y <= ey + 4) {
                int ty, k;
                SET(e->arg);
                for (ty = e->ty; ty < RH && (ty == e->ty || r->t[ty * RW + e->tx] == T_CRACK); ty++)
                    for (k = 0; k < e->arg2; k++) {
                        G.map[ty][e->tx + k] = T_EMPTY;
                        part_spawn(1, (e->tx + k) * TS + 8, ty * TS + 8, (k & 1) ? 1 : -1, -1, 30);
                    }
                G.bg_dirty = 1;
                G.shake = 12;
                sfx(SFX_SLAM);
                return;
            }
        }
    }
}

void player_update(void) {
    Player *p = &G.p;
    int dir = 0, steps, sd, px, py;
    int jumped = 0;
    int32_t nx, ny;

    if (p->hurt) p->hurt--;
    if (p->boost && (p->vy >= 0 || !--p->boost)) p->boost = 0;
    if (p->atk_cd) p->atk_cd--;
    if (p->dash_cd) p->dash_cd--;
    if (p->coyote) p->coyote--;
    if (p->jbuf) p->jbuf--;
    if (p->drop_t) p->drop_t--;
    if (HELD(K_LEFT)) dir = -1;
    if (HELD(K_RIGHT)) dir = 1;

    if (p->stun) {
        p->stun--;
    } else if (p->hook) {
        /* flying to an anchor */
        const Ent *e = &rooms[G.room].ent[p->hook_i];
        int dx = e->tx * TS + 8 - (PX(p->x) + 16), dy = e->ty * TS + 8 - (PX(p->y) + 16);
        int adx = dx < 0 ? -dx : dx, ady = dy < 0 ? -dy : dy, m = adx > ady ? adx : ady;
        p->hook--;
        if (m < 14 || !p->hook) {
            p->hook = 0;
            p->vy = -1400;
            p->vx = dir * WALK_MAX;
            p->air_dash = 0;
            p->air_jump = 0;
        } else {
            p->vx = (int32_t)dx * HOOK_V / m;
            p->vy = (int32_t)dy * HOOK_V / m;
            if (dx) p->face = dx < 0;
        }
    } else if (p->dash) {
        p->dash--;
        p->vx = p->face ? -RUSH_V : RUSH_V;
        p->vy = 0;
        if (!p->dash) { p->vx = p->face ? -300 : 300; p->dash_cd = 16; }
    } else if (p->cleave) {
        p->vy = CLEAVE_V;
        p->vx = dir * 200;
    } else {
        /* heal: hold X on solid ground */
        if (p->ground && HELD(K_X) && p->echo >= 33 && p->hp < p->maxhp && !dir) {
            p->heal++;
            p->vx = 0;
            if ((p->heal & 7) == 1) part_spawn(1, PX(p->x) + 8 + (int)(rnd() & 15), PX(p->y) + 28, 0, -1, 24);
            if (p->heal == 1) sfx(SFX_HEAL);
            if (p->heal >= 60) {
                p->heal = 0;
                p->echo -= 33;
                p->hp++;
                G.bot_dirty = 1;
                sfx(SFX_PICKUP);
                part_spawn(0, PX(p->x) + 16, PX(p->y) + 12, 0, 0, 12);
            }
        } else p->heal = 0;
        if (!p->heal) {
            if (dir) {
                p->face = dir < 0;
                p->vx += dir * WALK_ACC;
                if (p->vx > WALK_MAX) p->vx = WALK_MAX;
                if (p->vx < -WALK_MAX) p->vx = -WALK_MAX;
            } else {
                if (p->vx > WALK_ACC) p->vx -= WALK_ACC;
                else if (p->vx < -WALK_ACC) p->vx += WALK_ACC;
                else p->vx = 0;
            }
            if (PRESSED(K_DOWN) && p->ground) p->drop_t = 10;
            if (PRESSED(K_A)) p->jbuf = 6;
            if (p->jbuf && (p->ground || p->coyote)) {
                jumped = 1;
                p->vy = -JUMP_V;
                p->ground = 0; p->coyote = 0; p->jbuf = 0;
                sfx(SFX_JUMP);
            }
            if (!jumped && PRESSED(K_A) && !p->ground && HAS(F_CLOAK) && !p->air_jump) {
                p->air_jump = 1;
                p->jbuf = 0;
                p->vy = -AIRJUMP_V;
                sfx(SFX_JUMP);
                part_spawn(1, PX(p->x) + 10, PX(p->y) + 30, -1, 1, 16);
                part_spawn(1, PX(p->x) + 22, PX(p->y) + 30, 1, 1, 16);
            }
            if (!HELD(K_A) && p->vy < -JUMP_CUT && !p->boost) p->vy = -JUMP_CUT;
            if (PRESSED(K_B) && HELD(K_DOWN) && !p->ground && HAS(F_CLEAVE)) {
                p->cleave = 1;
                p->atk = 0;
                p->swing++;
                sfx(SFX_AXE);
            } else if (PRESSED(K_B) && !p->atk_cd) {
                p->atk = 14; p->atk_cd = 20; p->swing++;
                sfx(SFX_AXE);
            }
            if (PRESSED(K_R) && HAS(F_RUSH) && !p->dash_cd && (p->ground || !p->air_dash)) {
                if (dir) p->face = dir < 0;
                p->dash = RUSH_T;
                p->jbuf = 0;
                p->atk = 0;
                if (!p->ground) p->air_dash = 1;
                sfx(SFX_RUSH);
            }
            if (PRESSED(K_L) && HAS(F_HOOK)) {
                int a = find_anchor(dir);
                if (a >= 0) {
                    p->hook = 40;
                    p->hook_i = (uint8_t)a;
                    p->hook_last = (uint8_t)a;
                    p->atk = 0;
                    sfx(SFX_HOOK);
                }
            }
        }
    }
    if (p->atk) p->atk--;

    if (!p->dash && !p->hook && !p->cleave) {
        p->vy += GRAV;
        if (p->vy > FALL_MAX) p->vy = FALL_MAX;
    }

    /* move X one pixel at a time */
    nx = p->x + p->vx;
    steps = PX(nx) - PX(p->x);
    sd = steps < 0 ? -1 : 1;
    {
        int moved = 1;
        while (steps) {
            px = PX(p->x) + sd;
            py = PX(p->y);
            if (box_solid(px + HX, py + HY, HW, HH)) {
                moved = 0;
                p->vx = 0;
                if (p->dash) p->dash = 1;
                break;
            }
            p->x += sd * (1 << FP);
            steps -= sd;
        }
        if (moved) p->x = nx;
    }

    /* move Y */
    ny = p->y + p->vy;
    steps = PX(ny) - PX(p->y);
    sd = steps < 0 ? -1 : 1;
    {
        int moved = 1;
        while (steps) {
            px = PX(p->x);
            py = PX(p->y) + sd;
            if (sd > 0) {
                if (box_solid(px + HX, py + HY, HW, HH) || oneway_under(px, PX(p->y))) {
                    moved = 0;
                    if (p->cleave) {
                        break_crack();
                        p->cleave = 0;
                        p->atk = 8;
                        G.shake = 6;
                        sfx(SFX_SLAM);
                    } else if (p->vy > 1200) sfx(SFX_LAND);
                    p->vy = 0;
                    break;
                }
            } else if (box_solid(px + HX, py + HY, HW, HH)) {
                moved = 0;
                p->vy = 0;
                break;
            }
            p->y += sd * (1 << FP);
            steps -= sd;
        }
        if (moved) p->y = ny;
    }

    px = PX(p->x);
    py = PX(p->y);
    p->ground = 0;
    if (p->vy >= 0 && (box_solid(px + HX, py + HY + 1, HW, HH) || oneway_under(px, py))) p->ground = 1;
    if (p->ground) {
        p->coyote = 6;
        p->hook_last = 255;
        p->air_dash = 0;
        p->air_jump = 0;
        if (!box_hazard(px + HX - 8, py + HY, HW + 16, HH + 8)) { p->safe_x = p->x; p->safe_y = p->y; }
    }

    if (!p->dead && !p->dash && box_hazard(px + HX + 1, py + HY + 4, HW - 2, HH - 4)) hazard_reset();
    if (!p->dead && rooms[G.room].exits[3] == NONE && py > SH) hazard_reset();
}

void attack_check(void) {
    Player *p = &G.p;
    int i, px = PX(p->x), py = PX(p->y), ax, ay, aw = 34, ah = 34;
    int dmg = HAS(F_WHET) ? 2 : 1, bx, by, bw, bh;
    if (p->cleave) {
        ax = px + 2; ay = py + 20; aw = 28; ah = 24;
        dmg += 1;
    } else {
        if (!(p->atk <= 11 && p->atk >= 4)) return;
        ax = p->face ? px - 26 : px + 24;
        ay = py - 2;
    }
    for (i = 0; i < MAX_EN; i++) {
        Enemy *e = &G.en[i];
        if (!e->on || e->swing == p->swing) continue;
        if (overlap(ax, ay, aw, ah, PX(e->x) + 2, PX(e->y) + 2, 28, 28)) {
            e->swing = p->swing;
            enemy_hit(e, dmg);
            if (p->cleave) { p->cleave = 0; p->vy = -1500; }
        }
    }
    if (G.boss.active && G.boss.state != B_SLEEP && G.boss.state != B_DEAD && G.boss.swing != p->swing) {
        boss_box(&bx, &by, &bw, &bh);
        if (overlap(ax, ay, aw, ah, bx, by, bw, bh)) {
            G.boss.swing = p->swing;
            boss_hit(dmg);
            if (p->cleave) { p->cleave = 0; p->vy = -1500; }
        }
    }
}

void find_interaction(void) {
    const RoomDef *r = &rooms[G.room];
    int i, pcx = PX(G.p.x) + 16, pcy = PX(G.p.y) + 16;
    G.near_i = -1;
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        if (e->type == ENT_NPC || e->type == ENT_TABLET || e->type == ENT_LANTERN) {
            int dx = pcx - (e->tx * TS + 8), dy = pcy - (e->ty * TS + 8);
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dx < 28 && dy < 28) { G.near_i = (int8_t)i; return; }
        }
    }
}

static uint8_t npc_text(uint8_t who) {
    switch (who) {
    case 0:
        if (!HAS(F_MET_RINGER)) { SET(F_MET_RINGER); return TXT_RINGER1; }
        return HAS(F_BOSS0) ? TXT_RINGER3 : TXT_RINGER2;
    case 1:
        if (!HAS(F_MET_MINER)) { SET(F_MET_MINER); return TXT_MINER1; }
        return TXT_MINER2;
    case 2:
        if (!HAS(F_MET_CLERK)) { SET(F_MET_CLERK); return TXT_CLERK1; }
        return TXT_CLERK2;
    case 3:
        if (!HAS(F_MET_SMITH)) { SET(F_MET_SMITH); return TXT_SMITH1; }
        return TXT_SMITH2;
    default:
        if (!HAS(F_MET_HERMIT)) { SET(F_MET_HERMIT); return TXT_HERMIT1; }
        return TXT_HERMIT2;
    }
}

void interact(void) {
    const Ent *e = &rooms[G.room].ent[G.near_i];
    Player *p = &G.p;
    p->vx = 0;
    if (e->type == ENT_NPC) dialog(npc_text(e->arg), 0);
    else if (e->type == ENT_TABLET) dialog(e->arg, 0);
    else {
        G.save_room = G.room; G.save_tx = e->tx; G.save_ty = e->ty;
        p->hp = p->maxhp;
        save_game();
        sfx(SFX_SAVE);
        part_spawn(0, PX(p->x) + 16, PX(p->y) + 12, 0, 0, 12);
        part_spawn(1, PX(p->x) + 8, PX(p->y) + 28, -1, -1, 24);
        part_spawn(1, PX(p->x) + 24, PX(p->y) + 28, 1, -1, 24);
        G.msg = "SAVED";
        G.msg_t = 90;
        G.bot_dirty = 1;
    }
}

void check_items(void) {
    const RoomDef *r = &rooms[G.room];
    Player *p = &G.p;
    int i, px = PX(p->x) + HX, py = PX(p->y) + HY;
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        if (!G.item_on[i]) continue;
        if (overlap(px, py, HW, HH, e->tx * TS - 4, e->ty * TS - 8, 24, 24)) {
            G.item_on[i] = 0;
            sfx(SFX_PICKUP);
            G.bot_dirty = 1;
            if (e->type == ENT_ABILITY) {
                SET(e->arg);
                save_game();
                dialog(e->arg == F_RUSH ? TXT_GOT_RUSH : e->arg == F_HOOK ? TXT_GOT_HOOK : e->arg == F_CLEAVE ? TXT_GOT_CLEAVE : TXT_GOT_CLOAK, 0);
            } else if (e->type == ENT_SHARD) {
                SET(e->arg);
                p->maxhp++;
                p->hp = p->maxhp;
                save_game();
                dialog(TXT_GOT_SHARD, 0);
            } else if (e->type == ENT_WHET) {
                SET(e->arg);
                save_game();
                dialog(TXT_GOT_WHET, 0);
            } else if (e->type == ENT_BELL) {
                sfx(SFX_BELL);
                dialog(TXT_ENDING, 3);
            }
            return;
        }
    }
}
