/* Menuel - the five bosses. Box 64x64, floor top is row 13 = 208 px. */
#include "core.h"

#define FLOOR_Y (208 - 64)
#define XMIN 18
#define XMAX (SW - 64 - 18)
static const int16_t boss_hp[5] = { 20, 26, 30, 26, 44 };
static const uint8_t in_text[5] = { TXT_BOSS0_IN, TXT_BOSS1_IN, TXT_BOSS2_IN, TXT_BOSS3_IN, TXT_BOSS4_IN };
static const uint8_t out_text[5] = { TXT_BOSS0_OUT, TXT_BOSS1_OUT, TXT_BOSS2_OUT, TXT_BOSS3_OUT, TXT_BOSS4_OUT };

void boss_init(uint8_t id, int tx) {
    Boss *b = &G.boss;
    b->active = 1;
    b->id = id;
    b->maxhp = b->hp = boss_hp[id];
    b->state = B_SLEEP;
    b->x = (int32_t)(tx * TS) << FP;
    b->y = (int32_t)(id == 1 ? 40 : FLOOR_Y) << FP;
    b->face = 1;
}

void boss_box(int *x, int *y, int *w, int *h) {
    *x = PX(G.boss.x) + 6; *y = PX(G.boss.y) + 8; *w = 52; *h = 54;
}

static void clamp_x(void) {
    Boss *b = &G.boss;
    if (b->x < (XMIN << FP)) b->x = (int32_t)XMIN << FP;
    if (b->x > (XMAX << FP)) b->x = (int32_t)XMAX << FP;
}

static void wind(uint8_t next, int t) {
    G.boss.state = B_WIND;
    G.boss.next = next;
    G.boss.timer = (int16_t)t;
    sfx(SFX_ROAR);
}

static void waves(void) {
    int bx = PX(G.boss.x);
    proj_spawn(P_WAVE, bx - 8, FLOOR_Y + 40, -480, 0, 0);
    proj_spawn(P_WAVE, bx + 56, FLOOR_Y + 40, 480, 0, 0);
}

static void jump_at_player(int vy) {
    Boss *b = &G.boss;
    int d = (PX(G.p.x) + 16 - (PX(b->x) + 32));
    int v = d * 256 / 44;
    if (v > 900) v = 900;
    if (v < -900) v = -900;
    b->state = B_JUMP;
    b->vy = vy;
    b->vx = v;
    sfx(SFX_LAND);
}

static void pick_attack(int dist, int p2) {
    Boss *b = &G.boss;
    uint32_t r = rnd();
    switch (b->id) {
    case 0:
        wind(dist > 90 && (r & 1) ? B_CHARGE : B_JUMP, p2 ? 34 : 46);
        break;
    case 1:
        wind(B_DROP, p2 ? 30 : 44);
        break;
    case 2:
        if (r & 1) wind(B_THROW, p2 ? 30 : 42);
        else wind(dist > 90 ? B_CHARGE : B_JUMP, p2 ? 30 : 42);
        break;
    case 3:
        wind(B_JUMP, p2 ? 22 : 32);
        break;
    default:
        if ((r & 3) == 0) wind(B_THROW, p2 ? 26 : 36);
        else if ((r & 3) == 1) wind(B_RING, p2 ? 26 : 36);
        else wind(dist > 90 ? B_CHARGE : B_JUMP, p2 ? 26 : 36);
        break;
    }
}

void boss_update(void) {
    Boss *b = &G.boss;
    int bx = PX(b->x), by = PX(b->y), pcx = PX(G.p.x) + 16;
    int p2 = b->hp * 2 <= b->maxhp;
    int d = pcx - (bx + 32), ad = d < 0 ? -d : d;
    if (b->flash) b->flash--;

    switch (b->state) {
    case B_SLEEP:
        if (pcx > 70 && (G.p.ground || b->id == 3)) {
            close_boss_entry();
            b->state = b->id == 1 ? B_HOVER : B_IDLE;
            b->timer = 60;
            music_stop();
            dialog(in_text[b->id], 1);
        }
        return;
    case B_IDLE:
        b->face = d < 0;
        if (ad > 40) b->x += d > 0 ? (p2 ? 200 : 150) : (p2 ? -200 : -150);
        clamp_x();
        if (b->timer > 0) b->timer--;
        else pick_attack(ad, p2);
        break;
    case B_HOVER:     /* Rope Drowned drifts over the arena */
        b->face = d < 0;
        if (ad > 8) b->x += d > 0 ? (p2 ? 330 : 240) : (p2 ? -330 : -240);
        clamp_x();
        b->y = (int32_t)(36 + ((G.frame >> 4) & 7)) << FP;
        if (b->timer > 0) b->timer--;
        else pick_attack(ad, p2);
        break;
    case B_WIND:
        b->face = d < 0;
        if (b->timer > 0) { b->timer--; break; }
        switch (b->next) {
        case B_CHARGE:
            b->state = B_CHARGE;
            b->timer = 100;
            b->vx = b->face ? -(p2 ? 860 : 700) : (p2 ? 860 : 700);
            break;
        case B_JUMP:
            jump_at_player(b->id == 3 ? -2100 : -1700);
            break;
        case B_DROP:
            b->state = B_DROP;
            b->vy = 300;
            break;
        case B_THROW:
            b->state = B_RECOVER;
            b->timer = p2 ? 46 : 60;
            if (b->id == 2) {
                proj_spawn(P_ORB, bx + 28, by + 8, b->face ? -360 : 360, -1000, 1);
                proj_spawn(P_ORB, bx + 28, by + 8, b->face ? -600 : 600, -1200, 1);
                proj_spawn(P_ORB, bx + 28, by + 8, b->face ? -860 : 860, -1000, 1);
            } else {
                int i;
                for (i = 0; i < 3; i++)
                    proj_spawn(P_DROP, pcx - 44 + i * 44, -24 - i * 18, 0, 240, 1);
            }
            sfx(SFX_SLAM);
            break;
        case B_RING:
            b->state = B_RECOVER;
            b->timer = p2 ? 44 : 58;
            G.shake = 14;
            sfx(SFX_BELL);
            proj_spawn(P_ORB, bx + 28, by + 16, -640, -640, 0);
            proj_spawn(P_ORB, bx + 28, by + 16, 640, -640, 0);
            proj_spawn(P_ORB, bx + 28, by + 16, -760, 120, 0);
            proj_spawn(P_ORB, bx + 28, by + 16, 760, 120, 0);
            if (p2) waves();
            if (p2) {
                int i, any = 0;
                for (i = 0; i < MAX_EN; i++) if (G.en[i].on) any = 1;
                if (!any) spawn_enemy(6, bx < 180 ? 20 : 4, 5);
            }
            break;
        }
        break;
    case B_CHARGE:
        b->x += b->vx;
        bx = PX(b->x);
        if (bx <= XMIN || bx >= XMAX) {
            clamp_x();
            G.shake = 14;
            sfx(SFX_SLAM);
            b->state = B_STUN;
            b->timer = 80;
        } else if (--b->timer <= 0) {
            b->state = B_IDLE;
            b->timer = 24;
        }
        break;
    case B_JUMP:
        b->x += b->vx;
        b->y += b->vy;
        b->vy += 80;
        clamp_x();
        if (b->vy > 0 && b->y >= ((int32_t)FLOOR_Y << FP)) {
            b->y = (int32_t)FLOOR_Y << FP;
            b->vy = b->vx = 0;
            G.shake = 12;
            sfx(SFX_SLAM);
            waves();
            b->state = B_RECOVER;
            b->timer = p2 ? 44 : 60;
            if (b->id == 3) {
                b->count++;
                if (b->count >= 3) { b->count = 0; b->state = B_STUN; b->timer = 110; }
                else b->timer = p2 ? 20 : 30;
            }
        }
        break;
    case B_DROP:      /* Rope Drowned falls and sits on the floor, open to attack */
        b->vy += 90;
        b->y += b->vy;
        if (b->y >= ((int32_t)FLOOR_Y << FP)) {
            b->y = (int32_t)FLOOR_Y << FP;
            b->vy = 0;
            G.shake = 14;
            sfx(SFX_SLAM);
            if (p2) waves();
            proj_spawn(P_DROP, bx - 40, -20, 0, 200, 1);
            proj_spawn(P_DROP, bx + 90, -40, 0, 200, 1);
            b->state = B_STUN;
            b->timer = p2 ? 90 : 120;
        }
        break;
    case B_RISE:
        b->y -= 280;
        if (b->y <= (40 << FP)) { b->state = B_HOVER; b->timer = p2 ? 50 : 80; }
        break;
    case B_RECOVER:
        if (b->timer > 0) b->timer--;
        else { b->state = B_IDLE; b->timer = p2 ? 34 : 52; }
        break;
    case B_STUN:
        if (b->timer > 0) b->timer--;
        else if (b->id == 1) b->state = B_RISE;
        else { b->state = B_IDLE; b->timer = 40; }
        break;
    case B_DEAD:
        if (b->timer > 0) {
            b->timer--;
            if (!(b->timer & 7)) {
                part_spawn(1, bx + (int)(rnd() % 60), by + (int)(rnd() % 60), 0, -1, 24);
                sfx(SFX_KILL);
            }
            if (b->timer & 2) b->flash = 2;
            G.shake = 2;
        } else {
            uint8_t id = b->id;
            int i;
            b->active = 0;
            SET(F_BOSS0 + id);
            open_boss_doors();
            sfx(SFX_BELL);
            G.bot_dirty = 1;
            for (i = 0; i < rooms[G.room].nent; i++)
                if (rooms[G.room].ent[i].type == ENT_BELL) G.item_on[i] = 1;
            save_game();
            dialog(out_text[id], 2);
        }
        return;
    }
    bx = PX(b->x); by = PX(b->y);
    if (!G.p.hurt && !G.p.dead && overlap(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH, bx + 8, by + 12, 48, 50))
        player_hurt(1, pcx < bx + 32 ? -1 : 1);
}

void boss_hit(int dmg) {
    Boss *b = &G.boss;
    b->hp -= (int16_t)dmg;
    if (b->hp < 0) b->hp = 0;
    b->flash = 8;
    sfx(SFX_HIT);
    part_spawn(0, PX(b->x) + 32, PX(b->y) + 34, 0, 0, 12);
    if (G.p.echo < 99) { G.p.echo = G.p.echo > 88 ? 99 : G.p.echo + 11; G.bot_dirty = 1; }
    G.hitstop = 3;
    G.bot_dirty = 1;
    if (!b->hp) {
        int i;
        b->state = B_DEAD;
        b->timer = 110;
        sfx(SFX_ROAR);
        music_stop();
        for (i = 0; i < MAX_EN; i++) G.en[i].on = 0;
        for (i = 0; i < MAX_PROJ; i++) G.pr[i].on = 0;
    }
}
