/* Random input through every room with sanitizers on. Reports memory errors and broken game states. */
#include "../src/core.h"
#include <stdio.h>
#include <stdlib.h>

int host_init(const char *path);
void host_setup(int room, int tx, int ty, int maxhp, const uint8_t *flags);
void host_clear_save(void);
int plat_load(void *data, int len);

static uint32_t seed = 12345;
static uint32_t r32(void) { seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5; return seed; }

int main(int argc, char **argv) {
    long frames = argc > 1 ? atol(argv[1]) : 2000000, f;
    long embedded = 0, oob = 0, hpbad = 0, deaths = 0, rooms_changed = 0, bossfights = 0;
    long embed_by_room[NUM_ROOMS] = {0};
    uint16_t keys = 0;
    int last_room = -1, last_entry_frames = 0;
    uint32_t mode_stuck = 0;
    int last_mode = -1;
    if (!host_init("build/assets.bin")) return 2;
    for (f = 0; f < frames; f++) {
        if (r32() % 12 == 0) {
            static const uint16_t pool[] = { K_RIGHT, K_LEFT, K_A, K_B, K_RIGHT | K_A, K_LEFT | K_A, K_RIGHT | K_B, K_LEFT | K_B,
                K_DOWN, K_UP, K_R, K_L, K_X, K_DOWN | K_B, K_RIGHT | K_R, K_LEFT | K_R, K_RIGHT | K_L, K_START, 0 };
            keys = pool[r32() % (sizeof(pool) / sizeof(pool[0]))];
        }
        if (G.mode == M_TITLE) keys = (r32() & 1) ? K_A : 0;
        if (G.mode == M_TITLE && G.want_exit) G.want_exit = 0;
        /* jump to a random room with random progress now and then */
        if (f % 2400 == 0 && (G.mode == M_PLAY || G.mode == M_TITLE)) {
            uint8_t fl[8];
            int i, room = (int)(r32() % NUM_ROOMS);
            for (i = 0; i < 8; i++) fl[i] = (uint8_t)r32();
            /* spawn on the first free floor tile; a boss room's exit only opens once it is beaten,
               and rooms past it are only reachable then, so progress flags are kept consistent */
            {
                int tx, b, first_alive = 5;
                for (tx = 1; tx < RW - 1; tx++)
                    if (rooms[room].t[27 * RW + tx] == T_EMPTY && rooms[room].t[26 * RW + tx] == T_EMPTY && rooms[room].t[25 * RW + tx] == T_EMPTY && rooms[room].t[27 * RW + tx + 1] == T_EMPTY && rooms[room].t[28 * RW + tx] == T_ROCK) break;
                for (b = 0; b < 5; b++) { fl[F_BOSS0 >> 3] &= (uint8_t)~(1 << ((F_BOSS0 + b) & 7)); }
                {
                    int i2, own = -1;
                    for (i2 = 0; i2 < rooms[room].nent; i2++) if (rooms[room].ent[i2].type == ENT_BOSS) own = rooms[room].ent[i2].arg;
                    first_alive = own >= 0 ? own : (int)(rooms[room].theme >= 1) + (int)(rooms[room].theme >= 2) * 1 + (int)(rooms[room].theme >= 3) * 2;
                    /* rooms behind a boss door: Quench Room lies past the Founder */
                    if (!strcmp(rooms[room].name, "QUENCH ROOM")) first_alive = 3;
                    for (b = 0; b < first_alive; b++) fl[(F_BOSS0 + b) >> 3] |= (uint8_t)(1 << ((F_BOSS0 + b) & 7));
                }
                host_setup(room, tx < RW - 1 ? tx : 10, 27, 3 + (int)(r32() % 7), fl);
            }
        }
        core_step(keys);
        if (G.room != last_room) {
            rooms_changed++;
            if (last_room >= 0 && G.boss.active && box_solid(PX(G.p.x) + HX, PX(G.p.y) + HY, HW, HH))
                printf("entered boss room %s from %s inside a door\n", rooms[G.room].name, rooms[last_room].name);
            last_room = G.room; last_entry_frames = 0;
        }
        else last_entry_frames++;
        if (G.mode == M_DIALOG && G.dlg_page == 0 && G.dlg_pos == 1 && G.boss.active) bossfights++;
        if (G.mode == M_DEATH && G.timer == 90) deaths++;
        if (G.mode == M_PLAY) {
            int px = PX(G.p.x), py = PX(G.p.y);
            if (px < -40 || px > WW + 40 || py < -60 || py > WH + 60) { oob++; if (oob < 10) printf("out of bounds room %d at %d,%d\n", G.room, px, py); }
            if (G.p.hp > G.p.maxhp) hpbad++;
            /* setup() puts the player on a fixed tile, which may be inside rock: only count real entries */
            if (last_entry_frames > 30 && box_solid(px + HX, py + HY, HW, HH)) { embedded++; embed_by_room[G.room]++; }
        }
        if (G.mode == last_mode) mode_stuck++; else mode_stuck = 0;
        last_mode = G.mode;
        if (G.mode != M_PLAY && G.mode != M_DIALOG && G.mode != M_PAUSE && G.mode != M_TITLE && G.mode != M_CREDITS && mode_stuck > 600) {
            printf("stuck in mode %d, room %d\n", G.mode, G.room);
            return 3;
        }
        if (G.mode == M_CREDITS && mode_stuck > 300) keys = K_START;
    }
    printf("frames %ld, room changes %ld, deaths %ld, boss intros %ld\n", frames, rooms_changed, deaths, bossfights);
    printf("out of bounds %ld, health over max %ld, frames inside solid %ld\n", oob, hpbad, embedded);
    {
        int i;
        for (i = 0; i < NUM_ROOMS; i++) if (embed_by_room[i]) printf("  room %d (%s): %ld frames inside solid\n", i, rooms[i].name, embed_by_room[i]);
    }
    /* damaged save files must be refused */
    {
        SaveData s;
        uint8_t *b = (uint8_t *)&s;
        int i, bad = 0;
        G.save_room = 1; G.save_tx = 3; G.save_ty = 12; G.p.maxhp = 5;
        save_game();
        for (i = 0; i < (int)sizeof(s); i++) {
            plat_load(&s, sizeof(s));
            b[i] ^= 0x41;
            plat_save(&s, sizeof(s));
            if (has_save_file()) bad++;
            b[i] ^= 0x41;
            plat_save(&s, sizeof(s));
        }
        printf("damaged saves accepted: %d of %d\n", bad, (int)sizeof(s));
    }
    return 0;
}
