/* Menuel - 2DS XL / 3DS layer: input, framebuffers, NDSP audio, save file */
#include <3ds.h>
#include <stdio.h>
#include <malloc.h>
#include <string.h>
#include <sys/stat.h>
#include "core.h"

extern const uint8_t assets_bin[];
__asm__(".section .rodata\n.balign 4\n.global assets_bin\nassets_bin:\n.incbin \"build/assets.bin\"\n.previous\n");

#define SAVE_DIR "sdmc:/3ds/Menuel"
#define SAVE_PATH SAVE_DIR "/save.bin"
#define AUDIO_SAMPLES 1024
#define AUDIO_BUFS 4

static ndspWaveBuf wave[AUDIO_BUFS];
static int16_t *audio_mem;
static int audio_ok;

#ifdef BENCH
static double save_max;
#endif
void plat_save(const void *data, int len) {
    FILE *f;
#ifdef BENCH
    u64 t = svcGetSystemTick();
#endif
    mkdir("sdmc:/3ds", 0777);
    mkdir(SAVE_DIR, 0777);
    f = fopen(SAVE_PATH, "wb");
    if (f) { fwrite(data, 1, (size_t)len, f); fclose(f); }
#ifdef BENCH
    { double ms = (svcGetSystemTick() - t) / (SYSCLOCK_ARM11 / 1000.0); if (ms > save_max) save_max = ms; }
#endif
}

int plat_load(void *data, int len) {
    FILE *f = fopen(SAVE_PATH, "rb");
    int ok = 0;
    if (f) { ok = fread(data, 1, (size_t)len, f) == (size_t)len; fclose(f); }
    return ok;
}

static void audio_start(void) {
    int i;
    float mix[12] = { 0 };
    if (R_FAILED(ndspInit())) return;
    audio_mem = (int16_t *)linearAlloc(AUDIO_SAMPLES * AUDIO_BUFS * 2);
    if (!audio_mem) { ndspExit(); return; }
    ndspSetOutputMode(NDSP_OUTPUT_MONO);
    ndspChnReset(0);
    ndspChnSetInterp(0, NDSP_INTERP_LINEAR);
    ndspChnSetRate(0, AUDIO_RATE);
    ndspChnSetFormat(0, NDSP_FORMAT_MONO_PCM16);
    mix[0] = mix[1] = 1.0f;
    ndspChnSetMix(0, mix);
    memset(wave, 0, sizeof(wave));
    for (i = 0; i < AUDIO_BUFS; i++) {
        wave[i].data_vaddr = audio_mem + i * AUDIO_SAMPLES;
        wave[i].nsamples = AUDIO_SAMPLES;
        wave[i].status = NDSP_WBUF_DONE;
    }
    audio_ok = 1;
}

static void audio_pump(void) {
    int i;
    if (!audio_ok) return;
    for (i = 0; i < AUDIO_BUFS; i++) {
        if (wave[i].status == NDSP_WBUF_DONE) {
            audio_fill((int16_t *)wave[i].data_vaddr, AUDIO_SAMPLES);
            DSP_FlushDataCache(wave[i].data_vaddr, AUDIO_SAMPLES * 2);
            ndspChnWaveBufAdd(0, &wave[i]);
        }
    }
}

/* The LCDs are rotated: columns run bottom to top in the framebuffer. */
static void present(gfxScreen_t scr, const uint16_t *src, int w) {
    u16 *dst = (u16 *)gfxGetFramebuffer(scr, GFX_LEFT, NULL, NULL);
    int x, y;
    for (x = 0; x < w; x++) {
        u16 *col = dst + x * 240;
        const uint16_t *s = src + x;
        for (y = 239; y >= 0; y--) {
            col[y] = *s;
            s += w;
        }
    }
}

static uint16_t read_keys(void) {
    u32 k = hidKeysHeld();
    uint16_t o = 0;
    if (k & KEY_A) o |= K_A;
    if (k & KEY_B) o |= K_B;
    if (k & KEY_SELECT) o |= K_SELECT;
    if (k & KEY_START) o |= K_START;
    if (k & KEY_RIGHT) o |= K_RIGHT;     /* KEY_RIGHT includes the Circle Pad */
    if (k & KEY_LEFT) o |= K_LEFT;
    if (k & KEY_UP) o |= K_UP;
    if (k & KEY_DOWN) o |= K_DOWN;
    if (k & KEY_R) o |= K_R;
    if (k & KEY_L) o |= K_L;
    if (k & KEY_X) o |= K_X;
    return o;
}

#define TICKS_PER_MS (SYSCLOCK_ARM11 / 1000.0)

#ifdef BENCH
/* Benchmark build: drives every room with scripted input and writes sdmc:/3ds/Menuel/perf.txt */
static const uint16_t script[] = { K_RIGHT, K_RIGHT | K_A, K_RIGHT | K_B, K_RIGHT, K_LEFT | K_B, K_LEFT, K_LEFT | K_A, K_B };
void host_setup_bench(int room) {
    uint8_t fl[8];
    memset(fl, 0, sizeof(fl));
    fl[0] = 0x0F;   /* all abilities, no boss beaten: every boss room is live */
    memcpy(G.flags, fl, 8);
    G.p.maxhp = 9;
    G.save_room = (uint8_t)room; G.save_tx = 3; G.save_ty = 12; G.have_save = 0;
    respawn();
}
static void bench(void) {
    FILE *o;
    int r, f;
    u64 t0, t1, t2, t3;
    static double step_sum[NUM_ROOMS], step_max[NUM_ROOMS], pres_max, pres_sum, aud_max, aud_sum, all_max;
    long pres_n = 0;
    int16_t tmp[368];
    int worst = 0;
    mkdir("sdmc:/3ds", 0777);
    mkdir(SAVE_DIR, 0777);
    for (r = 0; r < NUM_ROOMS; r++) {
        host_setup_bench(r);
        for (f = 0; f < 240; f++) {
            uint16_t k = script[(f / 12) % 8];
            double st;
            if (G.mode == M_DIALOG) k = (f & 3) ? 0 : K_A;
            t0 = svcGetSystemTick();
            core_step(k);
            t1 = svcGetSystemTick();
            present(GFX_TOP, &fb_top[0][0], SW);
            present(GFX_BOTTOM, &fb_bot[0][0], BW);
            gfxFlushBuffers();
            t2 = svcGetSystemTick();
            audio_fill(tmp, 368);
            t3 = svcGetSystemTick();
            st = (t1 - t0) / TICKS_PER_MS;
            step_sum[r] += st;
            if (st > step_max[r]) step_max[r] = st;
            if ((t2 - t1) / TICKS_PER_MS > pres_max) pres_max = (t2 - t1) / TICKS_PER_MS;
            pres_sum += (t2 - t1) / TICKS_PER_MS; pres_n++;
            if ((t3 - t2) / TICKS_PER_MS > aud_max) aud_max = (t3 - t2) / TICKS_PER_MS;
            aud_sum += (t3 - t2) / TICKS_PER_MS;
            if ((t3 - t0) / TICKS_PER_MS > all_max) all_max = (t3 - t0) / TICKS_PER_MS;
            gfxSwapBuffers();
        }
        if (step_max[r] > step_max[worst]) worst = r;
    }
    o = fopen(SAVE_DIR "/perf.txt", "w");
    if (o) {
        fprintf(o, "units: ms at the 268 MHz tick, budget 16.67 ms per frame\n");
        fprintf(o, "present avg %.2f max %.2f\naudio avg %.2f max %.2f\nworst whole frame %.2f\nworst step room %s\nsave file write max %.2f\n",
                pres_sum / pres_n, pres_max, aud_sum / pres_n, aud_max, all_max, rooms[worst].name, save_max);
        for (r = 0; r < NUM_ROOMS; r++) fprintf(o, "%-18s step avg %.2f max %.2f\n", rooms[r].name, step_sum[r] / 240, step_max[r]);
        fclose(o);
    }
}
#endif

/* Performance readout on the 2DS XL itself: SELECT toggles it on the bottom screen. */
static void overlay(double step_ms, double total_ms, double worst_ms, int late) {
    char b[40];
    int i;
    for (i = 226; i < BH; i++) memset(fb_bot[i], 0, sizeof(fb_bot[0]));
    snprintf(b, sizeof(b), "%.1f/%.1f MAX %.1f LATE %d", step_ms, total_ms, worst_ms, late);
    draw_text(&fb_bot[0][0], BW, BH, 4, 229, b, 0xFFE0, 1);
}

int main(void) {
    static int show_perf, late;
    static double worst;
    int bot_frames = 2;
    osSetSpeedupEnable(true);
    gfxInit(GSP_RGB565_OES, GSP_RGB565_OES, false);
    gfxSetDoubleBuffering(GFX_TOP, true);
    gfxSetDoubleBuffering(GFX_BOTTOM, true);
    audio_start();
    core_init(assets_bin);
#ifdef BENCH
    bench();
    G.want_exit = 1;
#endif
    while (aptMainLoop() && !G.want_exit) {
        u64 t0, t1, t2;
        hidScanInput();
        if (hidKeysDown() & KEY_SELECT) {
            show_perf = !show_perf;
            worst = 0;
            late = 0;
            G.bot_dirty = 1;
        }
        t0 = svcGetSystemTick();
        core_step(read_keys());
        if (G.bot_dirty_seen) { G.bot_dirty_seen = 0; bot_frames = 2; }
        t1 = svcGetSystemTick();
        audio_pump();
        present(GFX_TOP, &fb_top[0][0], SW);
        if (show_perf) bot_frames = 2;
        if (bot_frames > 0) {   /* two buffers: a change must reach both */
            present(GFX_BOTTOM, &fb_bot[0][0], BW);
            bot_frames--;
        }
        t2 = svcGetSystemTick();
        if (show_perf) {
            double s = (t1 - t0) / TICKS_PER_MS, a = (t2 - t0) / TICKS_PER_MS;
            if (a > worst) worst = a;
            if (a > 16.6) late++;
            overlay(s, a, worst, late);
        }
        gfxFlushBuffers();
        gfxSwapBuffers();
        gspWaitForVBlank();
    }
    if (audio_ok) {
        ndspChnWaveBufClear(0);
        linearFree(audio_mem);
        ndspExit();
    }
    gfxExit();
    return 0;
}
