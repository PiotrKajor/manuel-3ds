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

void plat_save(const void *data, int len) {
    FILE *f;
    mkdir(SAVE_DIR, 0777);
    f = fopen(SAVE_PATH, "wb");
    if (f) { fwrite(data, 1, (size_t)len, f); fclose(f); }
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

int main(void) {
    static int bot_cleared;
    osSetSpeedupEnable(true);
    gfxInit(GSP_RGB565_OES, GSP_RGB565_OES, false);
    gfxSetDoubleBuffering(GFX_TOP, true);
    gfxSetDoubleBuffering(GFX_BOTTOM, true);
    audio_start();
    core_init(assets_bin);
    while (aptMainLoop() && !G.want_exit) {
        hidScanInput();
        core_step(read_keys());
        audio_pump();
        present(GFX_TOP, &fb_top[0][0], SW);
        present(GFX_BOTTOM, &fb_bot[0][0], BW);
        (void)bot_cleared;
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
