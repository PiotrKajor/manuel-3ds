/* Menuel - software renderer. The world spans both screens; sprites are drawn to whichever screens they touch. */
#include "core.h"

static uint16_t bg[WH][WW];
static uint8_t bg_room = 255;
static int shx, shy;
static const uint8_t *blob8;

uint16_t rgb(int r, int g, int b) {
    return (uint16_t)(((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3));
}

static inline uint16_t blend(uint16_t d, uint16_t s, uint32_t a) {   /* a: 0..32 */
    uint32_t rb = ((s & 0xF81Fu) * a + (d & 0xF81Fu) * (32 - a)) >> 5;
    uint32_t g = ((s & 0x07E0u) * a + (d & 0x07E0u) * (32 - a)) >> 5;
    return (uint16_t)((rb & 0xF81Fu) | (g & 0x07E0u));
}

/* Draw with the anchor at (x,y) on one framebuffer. */
static void blit_fb(uint16_t *fb, int fw, int fh, int id, int x, int y, int flip, int flash) {
    const SprDef *s = &spr_defs[id];
    const uint16_t *col = assets + s->off;
    const uint8_t *alpha = blob8 + s->aoff;
    int dx0 = flip ? x - s->ox - s->w : x + s->ox;
    int dy0 = y + s->oy;
    int yy, xx, w = s->w, h = s->h;
    int y0 = dy0 < 0 ? -dy0 : 0, y1 = dy0 + h > fh ? fh - dy0 : h;
    int x0 = dx0 < 0 ? -dx0 : 0, x1 = dx0 + w > fw ? fw - dx0 : w;
    if (x0 >= x1 || y0 >= y1) return;
    for (yy = y0; yy < y1; yy++) {
        uint16_t *dst = fb + (dy0 + yy) * fw + dx0;
        const uint16_t *c = col + yy * w;
        const uint8_t *a = alpha + yy * w;
        for (xx = x0; xx < x1; xx++) {
            int sx = flip ? w - 1 - xx : xx;
            uint32_t av = a[sx];
            if (av == 0) continue;
            if (flash) { dst[xx] = blend(dst[xx], 0xFFFF, av >> 3); continue; }
            if (av >= 248) dst[xx] = c[sx];
            else dst[xx] = blend(dst[xx], c[sx], (av + 4) >> 3);
        }
    }
}

/* Draw at world coordinates: appears on each screen it overlaps. */
static void wsprite(int id, int wx, int wy, int flip, int flash) {
    wx += shx; wy += shy;
    blit_fb(&fb_top[0][0], SW, SH, id, wx, wy, flip, flash);
    blit_fb(&fb_bot[0][0], BW, BH, id, wx - BOT_X, wy - BOT_Y, flip, flash);
}

static int text_width(const Font *f, const char *s) {
    int w = 0;
    for (; *s; s++) if (*s >= 32 && *s < 127) w += f->g[*s - 32].adv;
    return w;
}

static void text(uint16_t *fb, int fw, int fh, const Font *f, int x, int y, const char *s, uint16_t col) {
    int cx = x;
    for (; *s; s++) {
        if (*s == '\n') { cx = x; y += f->h + 2; continue; }
        if (*s >= 32 && *s < 127) {
            const Glyph *g = &f->g[*s - 32];
            const uint8_t *a = blob8 + g->off;
            int r, c;
            for (r = 0; r < f->h; r++) {
                int py = y + r;
                if (py < 0 || py >= fh) continue;
                for (c = 0; c < g->w; c++) {
                    uint32_t v = a[r * g->w + c];
                    int px = cx + c - 1;
                    if (v && px >= 0 && px < fw) fb[py * fw + px] = blend(fb[py * fw + px], col, (v + 4) >> 3);
                }
            }
            cx += g->adv;
        }
    }
}

static void shadow_text(uint16_t *fb, int fw, int fh, const Font *f, int x, int y, const char *s, uint16_t col) {
    text(fb, fw, fh, f, x + 1, y + 1, s, rgb(8, 6, 16));
    text(fb, fw, fh, f, x, y, s, col);
}

static void fill(uint16_t *fb, int fw, int x, int y, int w, int h, uint16_t col) {
    int yy, xx;
    for (yy = y; yy < y + h; yy++)
        for (xx = x; xx < x + w; xx++) fb[yy * fw + xx] = col;
}

static void fill_a(uint16_t *fb, int fw, int x, int y, int w, int h, uint16_t col, int a) {
    int yy, xx;
    for (yy = y; yy < y + h; yy++)
        for (xx = x; xx < x + w; xx++) fb[yy * fw + xx] = blend(fb[yy * fw + xx], col, (uint32_t)a);
}

/* LZ4 block decoder */
static void lz4_decode(const uint8_t *src, uint32_t n, uint8_t *dst) {
    const uint8_t *end = src + n;
    while (src < end) {
        uint32_t token = *src++, len = token >> 4;
        if (len == 15) { uint32_t b; do { b = *src++; len += b; } while (b == 255); }
        memcpy(dst, src, len);
        dst += len; src += len;
        if (src >= end) break;
        {
            uint32_t off = src[0] | ((uint32_t)src[1] << 8);
            const uint8_t *m;
            src += 2;
            len = token & 15;
            if (len == 15) { uint32_t b; do { b = *src++; len += b; } while (b == 255); }
            len += 4;
            m = dst - off;
            while (len--) *dst++ = *m++;
        }
    }
}

void render_bg(void) {
    const RoomDef *r = &rooms[G.room];
    if (bg_room != G.room) {
        lz4_decode(blob8 + r->bg_off, r->bg_len, (uint8_t *)bg);
        bg_room = G.room;
    }
    G.bg_dirty = 0;
}

static void copy_bg(void) {
    int y;
    int sx = shx, sy = shy;
    for (y = 0; y < SH; y++) {
        int src = y - sy;
        if (src < 0) src = 0;
        if (src >= WH) src = WH - 1;
        if (sx == 0) memcpy(fb_top[y], bg[src], sizeof(fb_top[0]));
        else if (sx > 0) { memcpy(fb_top[y] + sx, bg[src], (size_t)(SW - sx) * 2); }
        else memcpy(fb_top[y], bg[src] - sx, (size_t)(SW + sx) * 2);
    }
    for (y = 0; y < BH; y++) {
        int src = y + BOT_Y - sy;
        if (src < 0) src = 0;
        if (src >= WH) src = WH - 1;
        memcpy(fb_bot[y], bg[src] + BOT_X - sx, sizeof(fb_bot[0]));
    }
}

/* Doors and cracked floors change during play, so they are drawn over the painted room. */
static void draw_dynamic_tiles(int theme) {
    int x, y;
    for (y = 0; y < RH; y++)
        for (x = 0; x < RW; x++) {
            uint8_t t = G.map[y][x];
            if (t == T_DOOR) wsprite(S_DOOR0 + theme * 2, x * TS, y * TS, 0, 0);
            else if (t == T_CRACK) wsprite(S_CRACK0 + theme * 2, x * TS, y * TS, 0, 0);
        }
}

/* Ambient life: dust, bubbles, embers, snow. Positions come from the frame count, so they cost no state. */
static void ambient(int theme) {
    static const uint8_t cols[4][3] = { { 170, 200, 230 }, { 150, 240, 210 }, { 255, 170, 70 }, { 240, 244, 255 } };
    uint16_t c = rgb(cols[theme][0], cols[theme][1], cols[theme][2]);
    int i, n = 26;
    uint32_t f = G.frame;
    for (i = 0; i < n; i++) {
        uint32_t h = (uint32_t)i * 2654435761u;
        int sp = 1 + (int)((h >> 3) & 3);
        int x = (int)((h >> 8) % WW), y = (int)((h >> 18) % WH);
        int a = 10 + (int)((h >> 5) & 15);
        if (theme == 3) { y = (int)((y + f * sp / 2) % WH); x = (int)((x + f / 3 + (h & 7) * ((f >> 5) & 3)) % WW); }
        else if (theme == 2 || theme == 1) { y = (int)(((uint32_t)y + WH * 64 - f * sp / 2) % WH); x = (x + (int)((f >> 4) & 3)) % WW; }
        else { y = (int)((y + f / (uint32_t)(sp + 3)) % WH); x = (x + (int)((f >> 5) & 7)) % WW; }
        if (y < SH) {
            if (x < SW - 1) { fb_top[y][x] = blend(fb_top[y][x], c, (uint32_t)a); fb_top[y][x + 1] = blend(fb_top[y][x + 1], c, (uint32_t)a / 2); }
        } else if (x >= BOT_X && x < BOT_X + BW - 1) {
            fb_bot[y - BOT_Y][x - BOT_X] = blend(fb_bot[y - BOT_Y][x - BOT_X], c, (uint32_t)a);
            fb_bot[y - BOT_Y][x - BOT_X + 1] = blend(fb_bot[y - BOT_Y][x - BOT_X + 1], c, (uint32_t)a / 2);
        }
    }
}

static void draw_entities(void) {
    const RoomDef *r = &rooms[G.room];
    int i, pcx = PX(G.p.x) + PW / 2, pcy = PX(G.p.y) + PH / 2;
    int bob = ((G.frame >> 3) & 3);
    bob = bob == 3 ? 1 : bob;
    for (i = 0; i < r->nent; i++) {
        const Ent *e = &r->ent[i];
        int x = e->tx * TS + 8, y = (e->ty + 1) * TS;
        if (e->type == ENT_NPC) {
            wsprite(S_NPC0_0 + e->arg * 2 + ((G.frame >> 5) & 1), x, y, pcx < x, 0);
        } else if (e->type == ENT_ANCHOR) {
            int dx = x - pcx, dy = e->ty * TS + 8 - pcy;
            int lit = HAS(F_HOOK) && dx * dx + dy * dy < 170 * 170;
            wsprite(lit ? S_RING1 : S_RING0, x, e->ty * TS + 22, 0, 0);
        } else if (G.item_on[i]) {
            int id = -1;
            if (e->type == ENT_ABILITY) id = e->arg == F_RUSH ? S_IT_RUSH : e->arg == F_HOOK ? S_IT_HOOK : e->arg == F_CLEAVE ? S_IT_CLEAVE : S_IT_CLOAK;
            else if (e->type == ENT_SHARD) id = S_IT_SHARD0 + ((G.frame >> 4) & 1);
            else if (e->type == ENT_WHET) id = S_IT_WHET;
            else if (e->type == ENT_BELL) id = S_BELL0 + ((G.frame >> 4) & 1);
            if (id >= 0) wsprite(id, x, y - 4 - bob, 0, 0);
        }
    }
    if (G.near_i >= 0 && !G.p.stun) {
        const Ent *e = &r->ent[G.near_i];
        wsprite(S_UPMARK, e->tx * TS + 8, (e->ty + 1) * TS - 66 - bob, 0, 0);
    }
    for (i = 0; i < MAX_EN; i++) {
        Enemy *e = &G.en[i];
        if (e->on) {
            int f = (G.frame >> 3) & 3;
            if (e->kind == 2 || e->kind == 7) f = e->vy ? 2 : 0;
            wsprite(S_EN0_0 + e->kind * 4 + f, PX(e->x) + EW / 2, PX(e->y) + EH, e->dir ? 0 : 1, e->flash);
        }
    }
    if (G.boss.active) {
        Boss *b = &G.boss;
        int f;
        if (b->state == B_WIND || b->state == B_SLEEP) f = 2;
        else if (b->state == B_STUN) f = 5;
        else if (b->state == B_CHARGE || b->state == B_DROP) f = 3;
        else if (b->state == B_JUMP || b->state == B_RISE) f = 4;
        else f = (G.frame >> 5) & 1;
        wsprite(S_BOSS0_0 + b->id * 6 + f, PX(b->x) + BOSS_S / 2, PX(b->y) + BOSS_S, b->face ? 1 : 0, b->flash || (b->state == B_WIND && (b->timer & 4)));
    }
    for (i = 0; i < MAX_PROJ; i++) {
        Proj *q = &G.pr[i];
        if (q->on) {
            int base = q->kind == P_DROP ? S_DROP0 : q->kind == P_WAVE ? S_WAVE0 : S_ORB0;
            int off = q->kind == P_WAVE ? 18 : 12;
            wsprite(base + ((G.frame >> 2) & 1), PX(q->x), PX(q->y) + off, q->vx < 0, 0);
        }
    }
}

static void draw_player(void) {
    Player *p = &G.p;
    int f, px = PX(p->x) + PW / 2, py = PX(p->y) + PH;
    if (p->dead) return;
    if (p->hurt && !p->stun && ((p->hurt >> 2) & 1)) return;
    if (p->stun) f = S_M_HURT;
    else if (p->heal) f = S_M_HEAL0 + ((G.frame >> 4) & 1);
    else if (p->hook) f = S_M_HOOK;
    else if (p->dash) f = S_M_DASH0 + ((G.frame >> 2) & 1);
    else if (p->cleave) f = S_M_CLEAVE0 + ((G.frame >> 2) & 1);
    else if (p->atk) f = S_M_ATK0 + (p->atk > 11 ? 0 : p->atk > 9 ? 1 : p->atk > 6 ? 2 : p->atk > 3 ? 3 : 4);
    else if (!p->ground) f = p->vy < 0 ? S_M_RISE : S_M_FALL;
    else if (p->vx > 60 || p->vx < -60) f = S_M_RUN0 + ((G.frame >> 2) & 7);
    else f = S_M_IDLE0 + ((G.frame >> 5) & 3);
    if (p->hook) {
        const Ent *e = &rooms[G.room].ent[p->hook_i];
        int ax = e->tx * TS + 8, ay = e->ty * TS + 8, i, cy = py - PH / 2;
        for (i = 1; i < 7; i++)
            wsprite(S_LINK, px + (ax - px) * i / 7, cy + (ay - cy) * i / 7 + 6, 0, 0);
    }
    wsprite(f, px, py, p->face, 0);
}

static void draw_parts(void) {
    int i;
    for (i = 0; i < MAX_PART; i++) {
        Part *t = &G.pt[i];
        if (!t->life) continue;
        if (t->kind == 0) wsprite(S_SPARK0 + (t->life > 8 ? 0 : t->life > 4 ? 1 : 2), t->x, t->y + 20, 0, 0);
        else wsprite(S_MOTE0 + ((t->life >> 3) & 1), t->x, t->y + 5, 0, 0);
    }
}

static void dim(uint16_t *f, int n, int level) {
    int i;
    uint32_t k = (uint32_t)(8 - level);
    if (level <= 0) return;
    if (level >= 8) { memset(f, 0, (size_t)n * 2); return; }
    for (i = 0; i < n; i++) {
        uint32_t c = f[i];
        f[i] = (uint16_t)((((c & 0xF81Fu) * k >> 3) & 0xF81Fu) | (((c & 0x07E0u) * k >> 3) & 0x07E0u));
    }
}

static void dim_both(int level) {
    dim(&fb_top[0][0], SW * SH, level);
    dim(&fb_bot[0][0], BW * BH, level);
}

/* The HUD follows Menuel to whichever screen it is on. */
static void hud(void) {
    Player *p = &G.p;
    int on_bot = PX(p->y) + PH / 2 >= BOT_Y;
    uint16_t *fb = on_bot ? &fb_bot[0][0] : &fb_top[0][0];
    int fw = on_bot ? BW : SW, fh = on_bot ? BH : SH;
    int i, ox = 6, oy = 5;
    for (i = 0; i < p->maxhp; i++)
        blit_fb(fb, fw, fh, i < p->hp ? S_HEART_FULL : S_HEART_EMPTY, ox + 10 + i * 19, oy + 18, 0, 0);
    {
        int x = ox + 2, y = oy + 21, w = 78, fw2 = p->echo * w / 99;
        fill_a(fb, fw, x, y, w + 2, 7, rgb(8, 6, 16), 26);
        fill(fb, fw, x + 1, y + 1, fw2, 5, p->echo >= 33 ? rgb(226, 208, 250) : rgb(130, 100, 170));
    }
    if (G.boss.active && G.boss.state != B_SLEEP && G.boss.state != B_DEAD) {
        int w = 200, x = (fw - w) / 2, y = fh - 14, bw = G.boss.hp * w / G.boss.maxhp;
        fill(fb, fw, x - 2, y - 2, w + 4, 11, rgb(16, 11, 26));
        fill(fb, fw, x, y, bw, 7, rgb(220, 66, 78));
        fill(fb, fw, x, y, bw, 2, rgb(255, 150, 150));
    }
    if (G.banner > 0 && G.banner < 150 && G.mode == M_PLAY) {
        const char *n = rooms[G.room].name;
        int w = text_width(&font_mid, n);
        shadow_text(fb, fw, fh, &font_mid, (fw - w) / 2, 8, n, rgb(244, 236, 250));
    }
    if (G.msg_t) {
        G.msg_t--;
        shadow_text(fb, fw, fh, &font_mid, (fw - text_width(&font_mid, G.msg)) / 2, 34, G.msg, rgb(255, 235, 150));
    }
}

/* Dialogue goes on the screen Menuel is not on, so nothing is covered. */
static void dialog_box(void) {
    int on_bot = PX(G.p.y) + PH / 2 >= BOT_Y;
    uint16_t *fb = on_bot ? &fb_top[0][0] : &fb_bot[0][0];
    int fw = on_bot ? SW : BW, fh = SH;
    int w = 304, h = 68, x0 = (fw - w) / 2, y0 = fh - h - 12;
    char buf[140];
    const char *pg = text_pages[text_first[G.dlg_id] + G.dlg_page];
    int n = G.dlg_pos < 139 ? G.dlg_pos : 139;
    fill_a(fb, fw, x0 - 2, y0 - 2, w + 4, h + 4, rgb(168, 120, 200), 26);
    fill_a(fb, fw, x0, y0, w, h, rgb(14, 10, 26), 28);
    memcpy(buf, pg, (size_t)n);
    buf[n] = 0;
    text(fb, fw, fh, &font_small, x0 + 8, y0 + 7, buf, rgb(244, 236, 250));
    if (G.dlg_pos >= G.dlg_len && (G.frame & 16))
        text(fb, fw, fh, &font_mid, x0 + w - 16, y0 + h - 22, ">", rgb(255, 235, 150));
}

/* Pause: the map fills the lower screen, the top keeps the game frozen with a small menu. */
static void render_map(void) {
    static const uint8_t cols[4][3] = { { 120, 170, 200 }, { 70, 170, 140 }, { 220, 120, 60 }, { 170, 150, 220 } };
    uint16_t *f = &fb_bot[0][0];
    int i, x, y;
    fill(f, BW, 0, 0, BW, BH, rgb(14, 10, 26));
    text(f, BW, BH, &font_mid, 8, 4, rooms[G.room].name, rgb(244, 236, 250));
    for (i = 0; i < NUM_ROOMS; i++) {
        const RoomDef *r = &rooms[i];
        int seen = G.visited[i >> 3] & (1 << (i & 7));
        int cx = 6 + r->mx * 15, cy = 32 + r->my * 20;
        uint16_t c;
        if (!seen) continue;
        c = rgb(cols[r->theme][0], cols[r->theme][1], cols[r->theme][2]);
        fill(f, BW, cx, cy, 14, 18, c);
        fill(f, BW, cx + 1, cy + 1, 12, 16, rgb(cols[r->theme][0] / 3, cols[r->theme][1] / 3, cols[r->theme][2] / 3));
        for (x = 0; x < r->nent; x++) {
            if (r->ent[x].type == ENT_LANTERN) fill(f, BW, cx + 5, cy + 7, 4, 4, rgb(255, 220, 110));
            if (r->ent[x].type == ENT_BOSS) fill(f, BW, cx + 4, cy + 6, 6, 6, HAS(F_BOSS0 + r->ent[x].arg) ? rgb(120, 120, 130) : rgb(230, 70, 80));
        }
        if (r->exits[1] != NONE) fill(f, BW, cx + 13, cy + 8, 2, 2, c);
        if (r->exits[3] != NONE) fill(f, BW, cx + 6, cy + 17, 2, 3, c);
        if (i == G.room) {
            fill(f, BW, cx + 3, cy + 4, 8, 10, rgb(232, 224, 250));
            fill(f, BW, cx + 5, cy + 7, 1, 2, rgb(14, 10, 24));
            fill(f, BW, cx + 8, cy + 7, 1, 2, rgb(14, 10, 24));
        }
    }
    y = 150;
    fill(f, BW, 0, y - 4, BW, 1, rgb(70, 50, 100));
    {
        static const struct { uint8_t flag; int spr; const char *name; const char *key; } ab[4] = {
            { F_RUSH, S_IT_RUSH, "Rush", "R" }, { F_HOOK, S_IT_HOOK, "Hook", "L or tap" },
            { F_CLEAVE, S_IT_CLEAVE, "Cleave", "Down + B" }, { F_CLOAK, S_IT_CLOAK, "Cloak", "A in air" } };
        for (i = 0; i < 4; i++) {
            int ax = 40 + i * 80;
            if (HAS(ab[i].flag)) {
                blit_fb(f, BW, BH, ab[i].spr, ax, y + 36, 0, 0);
                text(f, BW, BH, &font_small, ax - text_width(&font_small, ab[i].name) / 2, y + 36, ab[i].name, rgb(244, 236, 250));
            } else {
                fill(f, BW, ax - 16, y + 4, 32, 32, rgb(24, 18, 40));
            }
        }
    }
    y = 208;
    fill(f, BW, 0, y - 2, BW, 1, rgb(70, 50, 100));
    {
        int bells = 0;
        for (i = 0; i < 4; i++) if (HAS(F_BOSS0 + i)) bells++;
        if (HAS(F_BOSS3) && bells) bells--;
        if (HAS(F_BOSS4)) bells++;
        for (i = 0; i < 4; i++)
            blit_fb(f, BW, BH, i < bells ? S_SBELL_ON : S_SBELL_OFF, 90 + i * 34, y + 30, 0, 0);
        text(f, BW, BH, &font_mid, 8, y + 6, "Bells", rgb(190, 170, 230));
        if (HAS(F_WHET)) blit_fb(f, BW, BH, S_IT_WHET, 292, y + 32, 0, 0);
    }
}

static void title_bg(void) {
    /* the summit room's painted sky serves both title screens */
    const RoomDef *r = &rooms[NUM_ROOMS - 1];
    if (bg_room != NUM_ROOMS - 1) { lz4_decode(blob8 + r->bg_off, r->bg_len, (uint8_t *)bg); bg_room = NUM_ROOMS - 1; }
    shx = shy = 0;
    copy_bg();
}

void render_text_bot(int x, int y, const char *s) { text(&fb_bot[0][0], BW, BH, &font_small, x, y, s, 0xFFE0); }

void render(void) {
    blob8 = (const uint8_t *)assets;
    shx = shy = 0;
    if (G.mode == M_TITLE) {
        const char *items[3];
        int n = 0, has = G.have_save, i;
        if (has) items[n++] = "Continue";
        items[n++] = "New Game";
        items[n++] = "Exit";
        title_bg();
        blit_fb(&fb_top[0][0], SW, SH, S_TITLE, 4, 24, 0, 0);
        shadow_text(&fb_top[0][0], SW, SH, &font_big, 262, 92, "Menuel", rgb(244, 236, 250));
        shadow_text(&fb_top[0][0], SW, SH, &font_mid, 250, 140, "and the Last Bell", rgb(190, 170, 230));
        for (i = 0; i < n; i++) {
            int y = 70 + i * 44, sel = i == G.menu;
            fill_a(&fb_bot[0][0], BW, 50, y, 220, 38, sel ? rgb(120, 92, 170) : rgb(14, 10, 26), 24);
            text(&fb_bot[0][0], BW, BH, &font_mid, (BW - text_width(&font_mid, items[i])) / 2, y + 8, items[i], sel ? rgb(255, 235, 150) : rgb(220, 210, 240));
        }
        return;
    }
    if (G.mode == M_CREDITS) {
        title_bg();
        blit_fb(&fb_top[0][0], SW, SH, S_TITLE, 0, 8, 0, 0);
        shadow_text(&fb_top[0][0], SW, SH, &font_big, 250, 70, "The End", rgb(244, 236, 250));
        shadow_text(&fb_bot[0][0], BW, BH, &font_mid, 60, 70, "Menuel and the Last Bell", rgb(220, 210, 240));
        shadow_text(&fb_bot[0][0], BW, BH, &font_small, 90, 100, "Thank you for playing", rgb(190, 170, 230));
        if (G.timer > 60) shadow_text(&fb_bot[0][0], BW, BH, &font_mid, 106, 180, "Press Start", rgb(255, 235, 150));
        return;
    }
    if (G.bg_dirty || bg_room != G.room) render_bg();
    if (G.shake) { shx = (G.frame & 1) ? 2 : -2; shy = (G.frame & 2) ? 2 : -2; }
    copy_bg();
    draw_dynamic_tiles(rooms[G.room].theme);
    ambient(rooms[G.room].theme);
    draw_entities();
    draw_player();
    draw_parts();
    shx = shy = 0;
    hud();
    if (G.mode == M_DIALOG) dialog_box();
    if (G.mode == M_PAUSE) {
        fill_a(&fb_top[0][0], SW, 130, 72, 140, 90, rgb(14, 10, 26), 28);
        text(&fb_top[0][0], SW, SH, &font_mid, 168, 80, "Paused", rgb(244, 236, 250));
        text(&fb_top[0][0], SW, SH, &font_mid, 166, 108, "Resume", G.menu == 0 ? rgb(255, 235, 150) : rgb(190, 170, 230));
        text(&fb_top[0][0], SW, SH, &font_mid, 178, 132, "Quit", G.menu == 1 ? rgb(255, 235, 150) : rgb(190, 170, 230));
        render_map();
    }
    if (G.mode == M_FADEOUT || G.mode == M_FADEIN) dim_both(G.fade);
    if (G.mode == M_DEATH) dim_both(G.timer < 40 ? 8 - G.timer / 5 : 0);
}
