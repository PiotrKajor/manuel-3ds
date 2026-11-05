/* Menuel and the Last Bell - platform free game core */
#ifndef CORE_H
#define CORE_H
#include <stdint.h>
#include <string.h>
#include "gen.h"

#define SW 400
#define SH 240
#define BW 320
#define BH 240
#define TS 16
#define RW 25
#define RH 15
#define FP 8                 /* positions are in 1/256 pixel */
#define PX(v) ((v) >> FP)

#define K_A 1
#define K_B 2
#define K_SELECT 4
#define K_START 8
#define K_RIGHT 16
#define K_LEFT 32
#define K_UP 64
#define K_DOWN 128
#define K_R 256
#define K_L 512
#define K_X 1024

/* player box inside the 32x32 sprite */
#define HX 9
#define HW 14
#define HY 4
#define HH 28

#define MAX_EN 6
#define MAX_PROJ 10
#define MAX_PART 12

enum { M_TITLE, M_PLAY, M_DIALOG, M_PAUSE, M_FADEOUT, M_FADEIN, M_DEATH, M_ENDING, M_CREDITS };
enum { B_SLEEP, B_IDLE, B_WIND, B_CHARGE, B_JUMP, B_RECOVER, B_STUN, B_HOVER, B_DROP, B_RISE, B_THROW, B_RING, B_DEAD };
enum { SFX_JUMP, SFX_AXE, SFX_HIT, SFX_HURT, SFX_RUSH, SFX_HEAL, SFX_PICKUP, SFX_SAVE, SFX_BLIP, SFX_ROAR, SFX_DIE, SFX_SLAM, SFX_KILL, SFX_SELECT, SFX_LAND, SFX_HOOK, SFX_BELL };
enum { P_DROP, P_WAVE, P_ORB };

typedef struct {
    int32_t x, y, vx, vy, safe_x, safe_y;
    uint8_t face, ground, coyote, jbuf, hp, maxhp, echo, hurt, stun, atk, atk_cd, swing;
    uint8_t dash, dash_cd, air_dash, air_jump, heal, dead, boost, cleave, hook, hook_i, hook_last, drop_t;
} Player;

typedef struct {
    uint8_t on, kind, hp, dir, flash, timer, swing, state;
    int32_t x, y, vx, vy, oy;
} Enemy;

typedef struct {
    uint8_t active, id, state, next, face, flash, swing, count;
    int16_t hp, maxhp, timer;
    int32_t x, y, vx, vy;
} Boss;

typedef struct { uint8_t on, kind, grav; int32_t x, y, vx, vy; } Proj;
typedef struct { uint8_t life, kind; int16_t x, y; int8_t vx, vy; } Part;

typedef struct {
    uint32_t magic;
    uint8_t flags[8];
    uint8_t visited[8];
    uint8_t room, tx, ty, maxhp;
    uint32_t sum;
} SaveData;

/* Everything the game knows lives here, so tests can snapshot and restore it. */
typedef struct {
    uint8_t mode, next_mode;
    uint16_t keys, old;
    uint32_t frame;
    uint32_t rng;
    uint8_t map[RH][RW];
    uint8_t room, pending_room, pending_dir, fade;
    uint8_t flags[8], visited[8];
    uint8_t save_room, save_tx, save_ty, have_save;
    Player p;
    Enemy en[MAX_EN];
    Boss boss;
    Proj pr[MAX_PROJ];
    Part pt[MAX_PART];
    uint8_t item_on[MAX_ENTS];
    uint8_t hitstop, shake, banner, want_exit;
    int8_t near_i;
    uint8_t dlg_id, dlg_page, dlg_after;
    uint16_t dlg_pos, dlg_len;
    uint8_t menu, title_t, bg_dirty, bot_dirty, bot_dirty_seen, timer, song, msg_t;
    const char *msg;
    uint16_t counters[4];    /* deaths, kills, hits taken, frames/3600 */
} Game;

extern Game G;
extern uint16_t fb_top[SH][SW];
extern uint16_t fb_bot[BH][BW];
extern const uint16_t *assets;
extern int g_headless;       /* tests: skip rendering */
extern int g_god;            /* tests: no damage (traversal only) */

#define HAS(f) (G.flags[(f) >> 3] & (1 << ((f) & 7)))
#define SET(f) (G.flags[(f) >> 3] |= (uint8_t)(1 << ((f) & 7)))
#define PRESSED(k) ((G.keys & ~G.old) & (k))
#define HELD(k) (G.keys & (k))

/* platform services */
void plat_save(const void *data, int len);
int plat_load(void *data, int len);

/* game.c */
void core_init(const void *blob);
void core_step(uint16_t keys);
uint32_t rnd(void);
uint8_t cell(int tx, int ty);
uint8_t solid_at(int px, int py);
int box_solid(int x, int y, int w, int h);
int box_hazard(int x, int y, int w, int h);
int oneway_under(int32_t x, int32_t y);
int overlap(int ax, int ay, int aw, int ah, int bx, int by, int bw, int bh);
void enter_room_now(uint8_t id);
void go_room(uint8_t id, uint8_t dir);
void dialog(uint8_t id, uint8_t after);
void save_game(void);
int load_game(void);
int has_save_file(void);
void open_boss_doors(void);
void close_boss_entry(void);
void part_spawn(uint8_t kind, int x, int y, int vx, int vy, uint8_t life);
void kill_fx(int x, int y);
void new_game(void);
void continue_game(void);
void respawn(void);

/* player.c */
void player_update(void);
void player_hurt(uint8_t amount, int dirx);
void attack_check(void);
void check_items(void);
void find_interaction(void);
void interact(void);

/* enemy.c */
void spawn_enemy(uint8_t kind, int tx, int ty);
void enemy_update(void);
void proj_spawn(uint8_t kind, int x, int y, int vx, int vy, uint8_t grav);
void proj_update(void);
void enemy_hit(Enemy *e, int dmg);

/* boss.c */
void boss_init(uint8_t id, int tx);
void boss_update(void);
void boss_hit(int dmg);
void boss_box(int *x, int *y, int *w, int *h);

/* render.c */
void render(void);
void render_bg(void);
void draw_text(uint16_t *fb, int stride, int maxh, int x, int y, const char *s, uint16_t col, int scale);
uint16_t rgb(int r, int g, int b);

/* audio.c */
void audio_reset(void);
void music_play(uint8_t song);
void music_stop(void);
void sfx(uint8_t id);
void audio_fill(int16_t *out, int n);
#define AUDIO_RATE 22050
#endif
