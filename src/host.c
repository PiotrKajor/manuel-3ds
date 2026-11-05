/* Test build: the same game as a shared library, driven from Python. */
#include "core.h"
#include <stdio.h>
#include <stdlib.h>

static uint8_t saved[256];
static int saved_len;
static void *blob;

void plat_save(const void *data, int len) {
    memcpy(saved, data, (size_t)len);
    saved_len = len;
}

int plat_load(void *data, int len) {
    if (saved_len != len) return 0;
    memcpy(data, saved, (size_t)len);
    return 1;
}

int host_init(const char *path) {
    FILE *f;
    long n;
    if (!blob) {
        f = fopen(path, "rb");
        if (!f) return 0;
        fseek(f, 0, SEEK_END); n = ftell(f); fseek(f, 0, SEEK_SET);
        blob = malloc((size_t)n);
        if (fread(blob, 1, (size_t)n, f) != (size_t)n) { fclose(f); return 0; }
        fclose(f);
    }
    core_init(blob);
    return 1;
}

void host_step(int keys) { core_step((uint16_t)keys); }
void host_run(int keys, int n) { while (n-- > 0) core_step((uint16_t)keys); }
void host_set_headless(int v) { g_headless = v; }
void host_set_god(int v) { g_god = v; }
int host_state_size(void) { return (int)sizeof(Game); }
void host_snapshot(void *dst) { memcpy(dst, &G, sizeof(G)); }
void host_restore(const void *src) { memcpy(&G, src, sizeof(G)); }
void host_clear_save(void) { saved_len = 0; }
void *host_fb_top(void) { return fb_top; }
void *host_fb_bot(void) { return fb_bot; }
void host_audio(int16_t *out, int n) { audio_fill(out, n); }
int host_render(void) { G.bg_dirty = 1; G.bot_dirty = 1; render(); return 0; }

/* read-only views for the tests */
int host_mode(void) { return G.mode; }
int host_room(void) { return G.room; }
int host_px(void) { return PX(G.p.x); }
int host_py(void) { return PX(G.p.y); }
int host_ground(void) { return G.p.ground; }
int host_hp(void) { return G.p.hp; }
int host_maxhp(void) { return G.p.maxhp; }
int host_echo(void) { return G.p.echo; }
int host_face(void) { return G.p.face; }
int host_hurt(void) { return G.p.hurt; }
int host_dead(void) { return G.p.dead; }
int host_has(int f) { return HAS(f) ? 1 : 0; }
int host_boss_active(void) { return G.boss.active; }
int host_boss_state(void) { return G.boss.state; }
int host_boss_hp(void) { return G.boss.hp; }
int host_boss_x(void) { return PX(G.boss.x); }
int host_boss_y(void) { return PX(G.boss.y); }
int host_boss_id(void) { return G.boss.id; }
int host_near(void) { return G.near_i; }
int host_hooking(void) { return G.p.hook; }
int host_atk_cd(void) { return G.p.atk_cd; }
int host_en(int i, int what) {
    Enemy *e = &G.en[i];
    return what == 0 ? e->on : what == 1 ? PX(e->x) : PX(e->y);
}
int host_pr(int i, int what) {
    Proj *q = &G.pr[i];
    return what == 0 ? q->on : what == 1 ? PX(q->x) : what == 2 ? PX(q->y) : what == 3 ? q->vx : q->vy;
}
int host_item_on(int i) { return G.item_on[i]; }
int host_num_rooms(void) { return NUM_ROOMS; }
int host_ent(int r, int i, int what) {
    const Ent *e = &rooms[r].ent[i];
    return what == 0 ? e->type : what == 1 ? e->tx : what == 2 ? e->ty : what == 3 ? e->arg : e->arg2;
}
int host_nent(int r) { return rooms[r].nent; }
int host_exit(int r, int side) { return rooms[r].exits[side]; }
void host_setup(int room, int tx, int ty, int maxhp, const uint8_t *flags) {
    /* tests only: start a room directly, as a lantern respawn would */
    memcpy(G.flags, flags, 8);
    G.p.maxhp = (uint8_t)maxhp;
    G.save_room = (uint8_t)room; G.save_tx = (uint8_t)tx; G.save_ty = (uint8_t)ty; G.have_save = 0;
    respawn();
    G.counters[0] = 0;
}
