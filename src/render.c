/* Menuel - software renderer. Top screen is the game, bottom screen is the map and status. */
#include "core.h"

static uint16_t bg[SH][SW];
static int8_t shx, shy;

uint16_t rgb(int r, int g, int b) {
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

static void blit(uint16_t *fb, int stride, int maxw, int maxh, int id, int x, int y, int flip, int flash) {
    const SprDef *s = &spr_defs[id];
    const uint16_t *src = assets + s->off;
    int yy, xx;
    for (yy = 0; yy < s->h; yy++) {
        int dy = y + yy;
        if (dy < 0 || dy >= maxh) continue;
        for (xx = 0; xx < s->w; xx++) {
            int dx = x + (flip ? s->w - 1 - xx : xx);
            uint16_t c = src[yy * s->w + xx];
            if (c == KEYCOL || dx < 0 || dx >= maxw) continue;
            fb[dy * stride + dx] = flash ? 0xFFFF : c;
        }
    }
}

#define TOP(id, x, y, flip, flash) blit(&fb_top[0][0], SW, SW, SH, id, (x) + shx, (y) + shy, flip, flash)

void draw_text(uint16_t *fb, int stride, int maxh, int x, int y, const char *s, uint16_t col, int scale) {
    int cx = x;
    for (; *s; s++) {
        if (*s == '\n') { cx = x; y += 8 * scale + 2; continue; }
        {
            int ch = *s;
            const uint8_t *g;
            int r, c, a, b;
            if (ch < 32 || ch >= 96) ch = 32;
            g = font5x7[ch - 32];
            for (r = 0; r < 7; r++)
                for (c = 0; c < 5; c++)
                    if (g[r] & (1 << (4 - c)))
                        for (a = 0; a < scale; a++)
                            for (b = 0; b < scale; b++) {
                                int py = y + r * scale + a, px = cx + c * scale + b;
                                if (py >= 0 && py < maxh && px >= 0 && px < stride) fb[py * stride + px] = col;
                            }
        }
        cx += 6 * scale;
    }
}

static void fill(uint16_t *fb, int stride, int x, int y, int w, int h, uint16_t col) {
    int yy, xx;
    for (yy = y; yy < y + h; yy++)
        for (xx = x; xx < x + w; xx++) fb[yy * stride + xx] = col;
}

static const uint16_t *tile_src(int theme, int idx) {
    return assets + TILE_OFF + (uint32_t)(theme * 33 + idx) * 256;
}

static void put_tile(int theme, int idx, int tx, int ty) {
    const uint16_t *s = tile_src(theme, idx);
    int y, x;
    for (y = 0; y < TS; y++)
        for (x = 0; x < TS; x++) {
            uint16_t c = s[y * TS + x];
            if (c != KEYCOL) bg[ty * TS + y][tx * TS + x] = c;
        }
}

static int rocky(int x, int y) {
    uint8_t t;
    if (x < 0 || x >= RW || y < 0 || y >= RH) return 1;
    t = G.map[y][x];
    return t == T_ROCK || t == T_DOOR || t == T_CRACK;
}

void render_bg(void) {
    const RoomDef *r = &rooms[G.room];
    int x, y, th = r->theme;
    memcpy(bg, assets + backdrop_off[th], sizeof(bg));
    for (y = 0; y < RH; y++)
        for (x = 0; x < RW; x++) {
            uint8_t t = G.map[y][x];
            if (t == T_EMPTY || t == T_ENTRY) continue;
            if (t == T_ROCK) {
                int m = (rocky(x, y - 1) ? 0 : 1) | (rocky(x, y + 1) ? 0 : 2) | (rocky(x - 1, y) ? 0 : 4) | (rocky(x + 1, y) ? 0 : 8);
                put_tile(th, m, x, y);
            } else put_tile(th, 16 + t, x, y);
        }
    G.bg_dirty = 0;
}

static void draw_entities(void) {
    const RoomDef *r = &rooms[G.room];
    int i, pcx = PX(G.p.x) + 16;
    int bob = ((G.frame >> 3) & 1) * 2;
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        int x = e->tx * TS, y = e->ty * TS - 16;
        if (e->type == ENT_NPC) {
            /* the smith shares the miner's art, the hermit the ringer's */
            static const uint8_t art[5] = { 0, 1, 2, 1, 0 };
            TOP(S_NPC0_0 + art[e->arg] * 2 + ((G.frame >> 5) & 1), x - 8, y, pcx < x + 8, 0);
        } else if (G.item_on[i]) {
            int id = -1;
            if (e->type == ENT_ABILITY) id = e->arg == F_RUSH ? S_IT_RUSH : e->arg == F_HOOK ? S_IT_HOOK : e->arg == F_CLEAVE ? S_IT_CLEAVE : S_IT_CLOAK;
            else if (e->type == ENT_SHARD) id = S_IT_SHARD + ((G.frame >> 4) & 1);
            else if (e->type == ENT_WHET) id = S_IT_WHET;
            else if (e->type == ENT_BELL) id = S_IT_BELL + ((G.frame >> 4) & 1);
            if (id >= 0) TOP(id, x - 8, y - bob, 0, 0);
        }
    }
    if (G.near_i >= 0 && !G.p.stun) {
        const Ent *e = &r->ent[G.near_i];
        TOP(S_UPMARK, e->tx * TS - 2, e->ty * TS - 40 - bob, 0, 0);
    }
    /* anchors in reach glow */
    if (HAS(F_HOOK)) {
        for (i = 0; i < r->nent; i++) {
            const Ent *e = &r->ent[i];
            if (e->type == ENT_ANCHOR) {
                int dx = e->tx * TS + 8 - pcx, dy = e->ty * TS + 8 - (PX(G.p.y) + 16);
                if (dx * dx + dy * dy < 136 * 136) TOP(S_UPMARK, e->tx * TS, e->ty * TS - 20 - bob, 0, 0);
            }
        }
    }
    for (i = 0; i < MAX_EN; i++) {
        Enemy *e = &G.en[i];
        if (e->on) TOP(S_EN0_0 + e->kind * 2 + ((G.frame >> 3) & 1), PX(e->x), PX(e->y), !e->dir, e->flash);
    }
    if (G.boss.active) {
        Boss *b = &G.boss;
        int f;
        if (b->state == B_WIND || b->state == B_STUN || b->state == B_SLEEP || b->state == B_DROP) f = 2;
        else if (b->state == B_CHARGE) f = 3;
        else if (b->state == B_JUMP || b->state == B_RISE) f = 4;
        else f = (G.frame >> 5) & 1;
        TOP(S_BOSS0_0 + b->id * 5 + f, PX(b->x), PX(b->y), b->face, b->flash || (b->state == B_WIND && (b->timer & 4)));
    }
    for (i = 0; i < MAX_PROJ; i++) {
        Proj *q = &G.pr[i];
        if (q->on) {
            int base = q->kind == P_DROP ? S_DROP0 : q->kind == P_WAVE ? S_WAVE0 : S_ORB0;
            TOP(base + ((G.frame >> 2) & 1), PX(q->x), PX(q->y), 0, 0);
        }
    }
}

static void draw_player(void) {
    Player *p = &G.p;
    int f, px = PX(p->x), py = PX(p->y);
    int vis = !(p->hurt && !p->stun && ((p->hurt >> 2) & 1));
    if (p->dead) return;
    if (p->stun) f = 10;
    else if (p->heal) f = 11;
    else if (p->dash || p->hook) f = 9;
    else if (p->atk || p->cleave) f = 8;
    else if (!p->ground) f = p->vy < 0 ? 6 : 7;
    else if (p->vx > 60 || p->vx < -60) f = 2 + ((G.frame >> 3) & 3);
    else f = (G.frame >> 5) & 1;
    if (p->hook) {
        const Ent *e = &rooms[G.room].ent[p->hook_i];
        int ax = e->tx * TS + 8, ay = e->ty * TS + 8, i;
        for (i = 1; i < 5; i++)
            TOP(S_LINK, px + 16 + (ax - px - 16) * i / 5 - 8, py + 16 + (ay - py - 16) * i / 5 - 16, 0, 0);
    }
    if (!vis) return;
    /* axe: carried on idle and run, swung on attack */
    if (p->cleave) TOP(S_AXE3, px - 4, py + 18, 0, 0);
    else if (p->atk >= 3) {
        int k = p->atk > 10 ? 0 : (p->atk > 6 ? 1 : 2);
        TOP(S_AXE0 + k, p->face ? px - 28 : px + 20, py - 4, p->face, 0);
    } else if (!p->dash && !p->hook && !p->heal) {
        TOP(S_AXE4, p->face ? px - 10 : px + 12, py - 8, p->face, 0);
    }
    TOP(S_MENUEL0 + f, px, py, p->face, 0);
}

static void draw_parts(void) {
    int i;
    for (i = 0; i < MAX_PART; i++) {
        Part *t = &G.pt[i];
        if (!t->life) continue;
        if (t->kind == 0) TOP(S_SPARK0 + (t->life > 8 ? 0 : t->life > 4 ? 1 : 2), t->x - 8, t->y - 16, 0, 0);
        else TOP(S_MOTE0 + ((t->life >> 3) & 1), t->x - 8, t->y - 16, 0, 0);
    }
}

static void dim_top(int level) {
    int i;
    uint16_t *f = &fb_top[0][0];
    /* level 0..8: halve brightness steps by masking */
    if (level <= 0) return;
    if (level >= 8) { memset(f, 0, sizeof(fb_top)); return; }
    {
        uint32_t k = (uint32_t)(8 - level);
        for (i = 0; i < SW * SH; i++) {
            uint32_t c = f[i];
            f[i] = (uint16_t)((((c & 0xF81Fu) * k >> 3) & 0xF81Fu) | (((c & 0x07E0u) * k >> 3) & 0x07E0u));
        }
    }
}

static void hud(void) {
    int i;
    Player *p = &G.p;
    for (i = 0; i < p->maxhp; i++)
        blit(&fb_top[0][0], SW, SW, SH, i < p->hp ? S_HEART_FULL : S_HEART_EMPTY, 6 + i * 16, 2, 0, 0);
    {
        int x = 6 + p->maxhp * 16 + 6, w = 66, fillw = p->echo * w / 99;
        fill(&fb_top[0][0], SW, x, 6, w + 2, 8, rgb(70, 50, 100));
        fill(&fb_top[0][0], SW, x + 1, 7, w, 6, rgb(16, 12, 30));
        fill(&fb_top[0][0], SW, x + 1, 7, fillw, 6, p->echo >= 33 ? rgb(220, 200, 250) : rgb(130, 100, 170));
    }
    if (G.boss.active && G.boss.state != B_SLEEP && G.boss.state != B_DEAD) {
        int w = 200, x = (SW - w) / 2, fw = G.boss.hp * w / G.boss.maxhp;
        fill(&fb_top[0][0], SW, x - 1, 226, w + 2, 10, rgb(240, 236, 250));
        fill(&fb_top[0][0], SW, x, 227, w, 8, rgb(30, 10, 20));
        fill(&fb_top[0][0], SW, x, 227, fw, 8, rgb(210, 60, 70));
    }
    if (G.banner > 0 && G.mode == M_PLAY && G.banner < 150) {
        const char *n = rooms[G.room].name;
        int w = (int)strlen(n) * 12;
        draw_text(&fb_top[0][0], SW, SH, (SW - w) / 2 + 1, 25, n, rgb(10, 8, 20), 2);
        draw_text(&fb_top[0][0], SW, SH, (SW - w) / 2, 24, n, rgb(244, 236, 250), 2);
    }
    if (G.msg_t) {
        G.msg_t--;
        draw_text(&fb_top[0][0], SW, SH, 170, 40, G.msg, rgb(255, 235, 150), 2);
    }
}

static void dialog_box(void) {
    int x0 = 16, y0 = 14, w = SW - 32, h = 80;
    char buf[100];
    const char *pg = text_pages[text_first[G.dlg_id] + G.dlg_page];
    int n = G.dlg_pos < 99 ? G.dlg_pos : 99;
    fill(&fb_top[0][0], SW, x0 - 2, y0 - 2, w + 4, h + 4, rgb(168, 120, 200));
    fill(&fb_top[0][0], SW, x0, y0, w, h, rgb(14, 10, 26));
    memcpy(buf, pg, (size_t)n);
    buf[n] = 0;
    draw_text(&fb_top[0][0], SW, SH, x0 + 10, y0 + 10, buf, rgb(244, 236, 250), 2);
    if (G.dlg_pos >= G.dlg_len && (G.frame & 16))
        draw_text(&fb_top[0][0], SW, SH, x0 + w - 18, y0 + h - 18, ">", rgb(255, 235, 150), 2);
}

/* ------------------------------------------------------------ bottom screen */
static void render_bottom(void) {
    uint16_t *f = &fb_bot[0][0];
    G.bot_dirty_seen = 1;
    int i, x, y;
    fill(f, BW, 0, 0, BW, BH, rgb(14, 10, 26));
    if (G.mode == M_TITLE) {
        draw_text(f, BW, BH, 28, 70, "A: CHOOSE  UP/DOWN: MOVE", rgb(168, 120, 200), 2);
        draw_text(f, BW, BH, 34, 120, "A STORY OF MENUEL AND", rgb(120, 100, 150), 2);
        draw_text(f, BW, BH, 70, 144, "THE LAST BELL", rgb(120, 100, 150), 2);
        G.bot_dirty = 0;
        return;
    }
    if (G.mode == M_CREDITS) { G.bot_dirty = 0; return; }
    {
        const RoomDef *cur = &rooms[G.room];
        static const uint8_t cols[4][3] = { { 120, 170, 200 }, { 70, 170, 140 }, { 220, 120, 60 }, { 170, 150, 220 } };
        draw_text(f, BW, BH, 8, 6, cur->name, rgb(244, 236, 250), 2);
        /* map: 20 columns, 5 rows */
        for (i = 0; i < NUM_ROOMS; i++) {
            const RoomDef *r = &rooms[i];
            int seen = G.visited[i >> 3] & (1 << (i & 7));
            int cx = 6 + r->mx * 15, cy = 30 + r->my * 18;
            uint16_t c;
            if (!seen) continue;
            c = rgb(cols[r->theme][0], cols[r->theme][1], cols[r->theme][2]);
            fill(f, BW, cx, cy, 14, 16, c);
            fill(f, BW, cx + 1, cy + 1, 12, 14, rgb(cols[r->theme][0] / 3, cols[r->theme][1] / 3, cols[r->theme][2] / 3));
            for (x = 0; x < r->nent; x++) {
                if (r->ent[x].type == ENT_LANTERN) fill(f, BW, cx + 5, cy + 6, 4, 4, rgb(255, 220, 110));
                if (r->ent[x].type == ENT_BOSS) {
                    uint16_t bc = HAS(F_BOSS0 + r->ent[x].arg) ? rgb(120, 120, 130) : rgb(230, 70, 80);
                    fill(f, BW, cx + 4, cy + 5, 6, 6, bc);
                }
            }
            /* door stubs show where a room still connects */
            if (r->exits[1] != NONE) fill(f, BW, cx + 13, cy + 7, 2, 2, c);
            if (r->exits[3] != NONE) fill(f, BW, cx + 6, cy + 15, 2, 3, c);
            if (i == G.room) {
                fill(f, BW, cx + 3, cy + 3, 8, 10, rgb(232, 224, 250));
                fill(f, BW, cx + 5, cy + 6, 1, 2, rgb(14, 10, 24));
                fill(f, BW, cx + 8, cy + 6, 1, 2, rgb(14, 10, 24));
            }
        }
        /* abilities and bells */
        y = 142;
        fill(f, BW, 0, y - 6, BW, 1, rgb(70, 50, 100));
        {
            static const struct { uint8_t flag; int spr; const char *key; const char *name; } ab[4] = {
                { F_RUSH, S_IT_RUSH, "R", "RUSH" }, { F_HOOK, S_IT_HOOK, "L", "HOOK" },
                { F_CLEAVE, S_IT_CLEAVE, "DN+B", "CLEAVE" }, { F_CLOAK, S_IT_CLOAK, "A+A", "CLOAK" } };
            for (i = 0; i < 4; i++) {
                int ax = 6 + i * 78;
                if (HAS(ab[i].flag)) {
                    blit(f, BW, BW, BH, ab[i].spr, ax + 18, y, 0, 0);
                    draw_text(f, BW, BH, ax + 8, y + 34, ab[i].name, rgb(244, 236, 250), 1);
                    draw_text(f, BW, BH, ax + 8, y + 44, ab[i].key, rgb(168, 120, 200), 1);
                } else {
                    fill(f, BW, ax + 18, y, 32, 32, rgb(24, 18, 40));
                    draw_text(f, BW, BH, ax + 8, y + 34, "?", rgb(90, 70, 120), 1);
                }
            }
        }
        y = 198;
        fill(f, BW, 0, y - 4, BW, 1, rgb(70, 50, 100));
        {
            int bells = 0;
            for (i = 0; i < 5; i++) if (HAS(F_BOSS0 + i)) bells++;
            draw_text(f, BW, BH, 8, y + 12, "BELLS", rgb(168, 120, 200), 2);
            /* the Founder and the Anvil guard the same bell */
            if (HAS(F_BOSS3) && bells) bells--;
            else if (HAS(F_BOSS2) && bells) bells--;
            for (i = 0; i < 4; i++) {
                if (i < bells) blit(f, BW, BW, BH, S_IT_BELL, 80 + i * 36, y, 0, 0);
                else fill(f, BW, 88 + i * 36, y + 10, 16, 16, rgb(28, 22, 44));
            }
            if (HAS(F_WHET)) blit(f, BW, BW, BH, S_IT_WHET, 278, y, 0, 0);
        }
    }
    G.bot_dirty = 0;
}

void render(void) {
    int i;
    shx = shy = 0;
    if (G.mode == M_TITLE) {
        const char *items[3];
        int n = 0, has = G.have_save;
        if (has) items[n++] = "CONTINUE";
        items[n++] = "NEW GAME";
        items[n++] = "EXIT";
        memcpy(fb_top, assets + backdrop_off[3], sizeof(fb_top));
        blit(&fb_top[0][0], SW, SW, SH, S_TITLE, 0, 30, 0, 0);
        draw_text(&fb_top[0][0], SW, SH, 238, 84, "MENUEL", rgb(244, 236, 250), 4);
        draw_text(&fb_top[0][0], SW, SH, 238, 122, "THE LAST BELL", rgb(190, 170, 230), 2);
        for (i = 0; i < n; i++) {
            draw_text(&fb_top[0][0], SW, SH, 262, 152 + i * 24, items[i], i == G.menu ? rgb(255, 235, 150) : rgb(190, 170, 230), 2);
            if (i == G.menu && (G.frame & 32)) draw_text(&fb_top[0][0], SW, SH, 244, 152 + i * 24, ">", rgb(255, 235, 150), 2);
        }
        if (G.bot_dirty) render_bottom();
        return;
    }
    if (G.mode == M_CREDITS) {
        memcpy(fb_top, assets + backdrop_off[3], sizeof(fb_top));
        blit(&fb_top[0][0], SW, SW, SH, S_TITLE, 0, 30, 0, 0);
        draw_text(&fb_top[0][0], SW, SH, 238, 92, "THE END", rgb(244, 236, 250), 3);
        draw_text(&fb_top[0][0], SW, SH, 238, 130, "MENUEL AND THE LAST BELL", rgb(190, 170, 230), 1);
        draw_text(&fb_top[0][0], SW, SH, 238, 146, "THANK YOU FOR PLAYING", rgb(190, 170, 230), 1);
        if (G.timer > 60) draw_text(&fb_top[0][0], SW, SH, 238, 186, "PRESS START", rgb(255, 235, 150), 2);
        if (G.bot_dirty) { fill(&fb_bot[0][0], BW, 0, 0, BW, BH, rgb(14, 10, 26)); G.bot_dirty = 0; G.bot_dirty_seen = 1; }
        return;
    }
    if (G.bg_dirty) render_bg();
    memcpy(fb_top, bg, sizeof(fb_top));
    if (G.shake) { shx = (int8_t)((G.frame & 1) ? 2 : -2); shy = (int8_t)((G.frame & 2) ? 2 : -2); }
    draw_entities();
    draw_player();
    draw_parts();
    shx = shy = 0;
    hud();
    if (G.mode == M_DIALOG) dialog_box();
    if (G.mode == M_PAUSE) {
        fill(&fb_top[0][0], SW, 130, 80, 140, 80, rgb(14, 10, 26));
        draw_text(&fb_top[0][0], SW, SH, 158, 88, "PAUSED", rgb(244, 236, 250), 2);
        draw_text(&fb_top[0][0], SW, SH, 160, 114, "RESUME", G.menu == 0 ? rgb(255, 235, 150) : rgb(190, 170, 230), 2);
        draw_text(&fb_top[0][0], SW, SH, 166, 134, "QUIT", G.menu == 1 ? rgb(255, 235, 150) : rgb(190, 170, 230), 2);
    }
    if (G.mode == M_FADEOUT || G.mode == M_FADEIN) dim_top(G.fade);
    if (G.mode == M_DEATH) dim_top(G.timer < 40 ? 8 - G.timer / 5 : 0);
    if (G.bot_dirty) render_bottom();
}
