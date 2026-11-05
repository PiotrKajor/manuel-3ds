/* Menuel - modes, rooms, collision, saving */
#include "core.h"

Game G;
uint16_t fb_top[SH][SW];
uint16_t fb_bot[BH][BW];
const uint16_t *assets;
int g_headless, g_god;

static const uint8_t theme_song[4] = { SONG_MINES, SONG_BELFRY, SONG_FOUNDRY, SONG_SUMMIT };
#define SAVE_MAGIC 0x324C454Du

uint32_t rnd(void) {
    uint32_t x = G.rng;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    G.rng = x;
    return x;
}

uint8_t cell(int tx, int ty) {
    const RoomDef *r = &rooms[G.room];
    if (ty < 0) return r->exits[2] == NONE ? T_ROCK : T_EMPTY;
    if (ty >= RH) return T_EMPTY;
    if (tx < 0) return r->exits[0] == NONE ? T_ROCK : T_EMPTY;
    if (tx >= RW) return r->exits[1] == NONE ? T_ROCK : T_EMPTY;
    return G.map[ty][tx];
}

static int is_solid(uint8_t t) { return t == T_ROCK || t == T_DOOR || t == T_CRACK; }

uint8_t solid_at(int px, int py) { return is_solid(cell(px >> 4, py >> 4)); }

int box_solid(int x, int y, int w, int h) {
    int tx, ty;
    for (ty = y >> 4; ty <= (y + h - 1) >> 4; ty++)
        for (tx = x >> 4; tx <= (x + w - 1) >> 4; tx++)
            if (is_solid(cell(tx, ty))) return 1;
    return 0;
}

int box_hazard(int x, int y, int w, int h) {
    int tx, ty;
    for (ty = y >> 4; ty <= (y + h - 1) >> 4; ty++)
        for (tx = x >> 4; tx <= (x + w - 1) >> 4; tx++)
            if (cell(tx, ty) == T_SPIKE) return 1;
    return 0;
}

int oneway_under(int32_t x, int32_t y) {
    int feet = (int)y + PH, tx;
    if (feet & 15) return 0;
    if (G.p.drop_t) return 0;
    for (tx = ((int)x + HX) >> 4; tx <= ((int)x + HX + HW - 1) >> 4; tx++)
        if (cell(tx, feet >> 4) == T_ONEWAY) return 1;
    return 0;
}

int overlap(int ax, int ay, int aw, int ah, int bx, int by, int bw, int bh) {
    return ax < bx + bw && bx < ax + aw && ay < by + bh && by < ay + ah;
}

void part_spawn(uint8_t kind, int x, int y, int vx, int vy, uint8_t life) {
    int i;
    for (i = 0; i < MAX_PART; i++)
        if (!G.pt[i].life) {
            G.pt[i].life = life; G.pt[i].kind = kind; G.pt[i].x = (int16_t)x; G.pt[i].y = (int16_t)y;
            G.pt[i].vx = (int8_t)vx; G.pt[i].vy = (int8_t)vy;
            return;
        }
}

void kill_fx(int x, int y) {
    sfx(SFX_KILL);
    part_spawn(0, x, y, 0, 0, 12);
    part_spawn(1, x - 8, y, -1, -1, 24);
    part_spawn(1, x + 8, y, 1, -1, 24);
    part_spawn(1, x, y - 6, 0, -2, 20);
}

/* ------------------------------------------------------------ rooms */
static void load_room(uint8_t id) {
    const RoomDef *r = &rooms[id];
    int i, x, y;
    G.room = id;
    G.visited[id >> 3] |= (uint8_t)(1 << (id & 7));
    for (y = 0; y < RH; y++)
        for (x = 0; x < RW; x++) {
            uint8_t t = r->t[y * RW + x];
            G.map[y][x] = t == T_ENTRY ? T_EMPTY : t;
        }
    memset(G.en, 0, sizeof(G.en));
    memset(G.pr, 0, sizeof(G.pr));
    memset(G.pt, 0, sizeof(G.pt));
    memset(&G.boss, 0, sizeof(G.boss));
    memset(G.item_on, 0, sizeof(G.item_on));
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        switch (e->type) {
        case ENT_ENEMY: spawn_enemy(e->arg, e->tx, e->ty); break;
        case ENT_ABILITY: case ENT_SHARD: case ENT_WHET:
            G.item_on[i] = !HAS(e->arg);
            break;
        case ENT_BELL:
            G.item_on[i] = HAS(F_BOSS4) && !HAS(F_ENDED);
            break;
        case ENT_CRACK:
            if (HAS(e->arg)) {
                int k;
                for (y = e->ty; y < RH && (y == e->ty || r->t[y * RW + e->tx] == T_CRACK); y++)
                    for (k = 0; k < e->arg2; k++) G.map[y][e->tx + k] = T_EMPTY;
            }
            break;
        case ENT_BOSS:
            if (HAS(F_BOSS0 + e->arg)) open_boss_doors();
            else boss_init(e->arg, e->tx);
            break;
        }
    }
    G.banner = 150;
    G.bg_dirty = 1;
    G.near_i = -1;
}

void open_boss_doors(void) {
    int x, y;
    for (y = 0; y < RH; y++)
        for (x = 0; x < RW; x++)
            if (G.map[y][x] == T_DOOR) G.map[y][x] = T_EMPTY;
}

void close_boss_entry(void) {
    const RoomDef *r = &rooms[G.room];
    int x, y;
    for (y = 0; y < RH; y++)
        for (x = 0; x < RW; x++)
            if (r->t[y * RW + x] == T_ENTRY) G.map[y][x] = T_DOOR;
}

/* The bottom screen is narrower: side doors down there open at its own edges. */
static int edge_left(int cy) { return cy >= BOT_Y ? BOT_X : 0; }
static int edge_right(int cy) { return cy >= BOT_Y ? BOT_X + BW : WW; }

/* Never start a room inside a wall. */
static void unstick(void) {
    Player *p = &G.p;
    int d;
    for (d = 1; d < 64 && box_solid(PX(p->x) + HX, PX(p->y) + HY, HW, HH); d++) {
        int32_t ox = p->x;
        p->x = ox + (int32_t)d * (1 << FP);
        if (!box_solid(PX(p->x) + HX, PX(p->y) + HY, HW, HH)) break;
        p->x = ox - (int32_t)d * (1 << FP);
        if (!box_solid(PX(p->x) + HX, PX(p->y) + HY, HW, HH)) break;
        p->x = ox;
    }
}

static void place_for_entry(uint8_t dir) {
    Player *p = &G.p;
    int cy = PX(p->y) + PH / 2;
    p->hook = 0;
    p->hook_last = 255;
    if (dir == 1) p->x = (int32_t)(edge_left(cy) + 4 - PW / 2) * (1 << FP);
    else if (dir == 2) p->x = (int32_t)(edge_right(cy) - 4 - PW / 2) * (1 << FP);
    else if (dir == 3) {                        /* came up through the floor */
        p->y = (int32_t)(WH - PH) * (1 << FP);
        p->vy = -(9 << FP);
        p->boost = 30;
        p->drop_t = 0;
    } else if (dir == 4) {                      /* fell through the ceiling */
        p->y = (int32_t)(-30) * (1 << FP);
    }
    if (dir == 1 || dir == 2) p->vy = 0;
    unstick();
    p->safe_x = p->x; p->safe_y = p->y;
}

static void song_for_room(void) {
    uint8_t s = theme_song[rooms[G.room].theme];
    if (!(G.boss.active && G.boss.state != B_SLEEP)) music_play(s);
}

void enter_room_now(uint8_t id) {
    load_room(id);
    song_for_room();
}

void go_room(uint8_t id, uint8_t dir) {
    if (G.mode != M_PLAY) return;
    G.pending_room = id;
    G.pending_dir = dir;
    G.mode = M_FADEOUT;
    G.fade = 0;
}

void dialog(uint8_t id, uint8_t after) {
    G.dlg_id = id;
    G.dlg_page = 0;
    G.dlg_pos = 0;
    G.dlg_len = (uint16_t)strlen(text_pages[text_first[id]]);
    G.dlg_after = after;
    G.mode = M_DIALOG;
}

/* ------------------------------------------------------------ saving */
static uint32_t sum_save(const SaveData *s) {
    const uint8_t *b = (const uint8_t *)s;
    uint32_t v = 0x5A17;
    size_t i;
    for (i = 0; i < offsetof(SaveData, sum); i++) v = v * 31 + b[i];
    return v;
}

void save_game(void) {
    SaveData s;
    memset(&s, 0, sizeof(s));
    s.magic = SAVE_MAGIC;
    memcpy(s.flags, G.flags, 8);
    memcpy(s.visited, G.visited, 8);
    s.room = G.save_room; s.tx = G.save_tx; s.ty = G.save_ty; s.maxhp = G.p.maxhp;
    s.sum = sum_save(&s);
    plat_save(&s, sizeof(s));
    G.have_save = 1;
}

static int read_save(SaveData *s) {
    if (!plat_load(s, sizeof(*s))) return 0;
    return s->magic == SAVE_MAGIC && s->sum == sum_save(s) && s->room < NUM_ROOMS;
}

int has_save_file(void) {
    SaveData s;
    return read_save(&s);
}

int load_game(void) {
    SaveData s;
    if (!read_save(&s)) return 0;
    memcpy(G.flags, s.flags, 8);
    memcpy(G.visited, s.visited, 8);
    G.save_room = s.room; G.save_tx = s.tx; G.save_ty = s.ty; G.p.maxhp = s.maxhp;
    G.have_save = 1;
    return 1;
}

/* ------------------------------------------------------------ flow */
static void reset_player(void) {
    uint8_t mh = G.p.maxhp ? G.p.maxhp : 5;
    memset(&G.p, 0, sizeof(G.p));
    G.p.maxhp = mh;
    G.p.hp = mh;
    G.p.hook_i = 255;
    G.p.hook_last = 255;
    G.p.x = (int32_t)(G.save_tx * TS + 8 - PW / 2) * (1 << FP);
    G.p.y = (int32_t)((G.save_ty + 1) * TS - PH) * (1 << FP);
    G.p.safe_x = G.p.x; G.p.safe_y = G.p.y;
}

void new_game(void) {
    const RoomDef *r = &rooms[0];
    int i;
    memset(G.flags, 0, 8);
    memset(G.visited, 0, 8);
    G.p.maxhp = 5;
    G.save_room = 0; G.save_tx = 8; G.save_ty = 27; G.have_save = 0;
    for (i = 0; i < r->nent; i++)
        if (r->ent[i].type == ENT_START) { G.save_tx = r->ent[i].tx; G.save_ty = r->ent[i].ty; }
    reset_player();
    enter_room_now(0);
    dialog(TXT_INTRO, 0);
    G.fade = 0;
}

void continue_game(void) {
    if (!load_game()) { new_game(); return; }
    reset_player();
    enter_room_now(G.save_room);
    unstick();
    G.p.safe_x = G.p.x; G.p.safe_y = G.p.y;
    G.mode = M_FADEIN;
    G.fade = 8;
    G.next_mode = M_PLAY;
}

void respawn(void) {
    G.counters[0]++;
    if (G.have_save) load_game();
    reset_player();
    enter_room_now(G.save_room);
    unstick();
    G.p.safe_x = G.p.x; G.p.safe_y = G.p.y;
    G.mode = M_FADEIN;
    G.fade = 8;
    G.next_mode = M_PLAY;
}

static void update_play(void) {
    Player *p = &G.p;
    const RoomDef *r = &rooms[G.room];
    int i, cx, cy;
    if (G.hitstop) { G.hitstop--; return; }
    if (PRESSED(K_START)) { G.mode = M_PAUSE; G.menu = 0; sfx(SFX_SELECT); return; }
    player_update();
    if (G.mode != M_PLAY) return;
    if (p->dead) { G.mode = M_DEATH; G.timer = 90; music_stop(); return; }
    attack_check();
    enemy_update();
    if (G.boss.active) boss_update();
    if (G.mode != M_PLAY) return;
    proj_update();
    find_interaction();
    check_items();
    if (G.mode != M_PLAY) return;
    if (G.near_i >= 0 && PRESSED(K_UP) && p->ground && !p->stun) interact();
    if (G.mode != M_PLAY) return;
    for (i = 0; i < MAX_PART; i++)
        if (G.pt[i].life) {
            G.pt[i].life--;
            G.pt[i].x += G.pt[i].vx;
            G.pt[i].y += G.pt[i].vy;
        }
    if (G.banner) G.banner--;
    if (G.shake) G.shake--;
    cx = PX(p->x) + PW / 2;
    cy = PX(p->y) + PH / 2;
    if (cx < edge_left(cy) && r->exits[0] != NONE) go_room(r->exits[0], 2);
    else if (cx >= edge_right(cy) && r->exits[1] != NONE) go_room(r->exits[1], 1);
    else if (cy < 0 && p->vy < 0 && r->exits[2] != NONE) go_room(r->exits[2], 3);
    else if (cy >= WH && r->exits[3] != NONE) go_room(r->exits[3], 4);
}

static void update_dialog(void) {
    int n = HELD(K_A | K_B) ? 3 : 1;
    const char *pg = text_pages[text_first[G.dlg_id] + G.dlg_page];
    if (G.dlg_pos < G.dlg_len) {
        while (n-- && G.dlg_pos < G.dlg_len) {
            if (pg[G.dlg_pos] != ' ' && (G.dlg_pos & 1)) sfx(SFX_BLIP);
            G.dlg_pos++;
        }
    } else if (PRESSED(K_A | K_B | K_START) || (G.touch && !G.touch_old)) {
        sfx(SFX_SELECT);
        G.dlg_page++;
        if (G.dlg_page >= text_count[G.dlg_id]) {
            G.mode = M_PLAY;
            if (G.dlg_after == 1) {
                music_play(G.boss.id == 4 ? SONG_FINAL : SONG_BOSS);
                sfx(SFX_ROAR);
                G.shake = 20;
            } else if (G.dlg_after == 2) {
                music_play(theme_song[rooms[G.room].theme]);
            } else if (G.dlg_after == 3) {
                G.mode = M_CREDITS;
                G.timer = 0;
                SET(F_ENDED);
                save_game();
                music_play(SONG_END);
            }
        } else {
            G.dlg_pos = 0;
            G.dlg_len = (uint16_t)strlen(text_pages[text_first[G.dlg_id] + G.dlg_page]);
        }
    }
}

static void title_choose(int item) {
    int has = G.have_save;
    int choice = item + (has ? 0 : 1);   /* 0 continue, 1 new, 2 exit */
    sfx(SFX_PICKUP);
    if (choice == 0) continue_game();
    else if (choice == 1) new_game();
    else G.want_exit = 1;
}

static void update_title(void) {
    int has = G.have_save;
    int n = has ? 3 : 2;
    G.title_t++;
    if (PRESSED(K_UP)) { G.menu = (uint8_t)((G.menu + n - 1) % n); sfx(SFX_SELECT); }
    if (PRESSED(K_DOWN)) { G.menu = (uint8_t)((G.menu + 1) % n); sfx(SFX_SELECT); }
    if (PRESSED(K_A | K_START)) { title_choose(G.menu); return; }
    if (G.touch && !G.touch_old) {
        int i = (G.ty - 70) / 44;
        if (G.ty >= 70 && i < n) { G.menu = (uint8_t)i; title_choose(i); }
    }
}

static void to_title(void) {
    G.mode = M_TITLE;
    G.have_save = has_save_file();
    G.menu = 0;
    G.bg_dirty = 0;
    music_play(SONG_TITLE);
}

void core_init(const void *blob) {
    assets = (const uint16_t *)blob;
    memset(&G, 0, sizeof(G));
    G.rng = 0x1234567;
    audio_reset();
    to_title();
}

void core_touch(int active, int x, int y) {
    G.touch_old = G.touch;
    G.touch = (uint8_t)active;
    G.tx = (int16_t)x;
    G.ty = (int16_t)y;
}

void core_step(uint16_t keys) {
    G.old = G.keys;
    G.keys = keys;
    G.frame++;
    switch (G.mode) {
    case M_TITLE: update_title(); break;
    case M_PLAY: update_play(); break;
    case M_DIALOG: update_dialog(); break;
    case M_PAUSE:
        if (PRESSED(K_UP | K_DOWN)) { G.menu ^= 1; sfx(SFX_SELECT); }
        if (PRESSED(K_START)) G.mode = M_PLAY;
        if (PRESSED(K_A)) { if (G.menu) to_title(); else G.mode = M_PLAY; }
        break;
    case M_FADEOUT:
        if (++G.fade >= 8) {
            load_room(G.pending_room);
            place_for_entry(G.pending_dir);
            song_for_room();
            G.mode = M_FADEIN;
            G.next_mode = M_PLAY;
            G.fade = 8;
        }
        break;
    case M_FADEIN:
        if (G.fade) G.fade--;
        else G.mode = G.next_mode;
        break;
    case M_DEATH:
        if (G.timer) {
            G.timer--;
            if (G.timer % 8 == 0) part_spawn(1, PX(G.p.x) + PW / 2, PX(G.p.y) + PH / 2, (int)(rnd() % 5) - 2, -2, 24);
        } else respawn();
        break;
    case M_CREDITS:
        if (G.timer < 255) G.timer++;
        if (G.timer > 60 && PRESSED(K_A | K_START)) to_title();
        break;
    default: break;
    }
    if (!g_headless) render();
}
