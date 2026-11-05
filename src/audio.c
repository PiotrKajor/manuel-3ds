/* Manuel - small chiptune synth: lead square, bass triangle, noise drums, two sfx voices */
#include "core.h"

#define TICK_HZ 60
typedef struct { const uint8_t *p; uint8_t t; uint8_t note; uint32_t phase, step; int16_t env; } Voice;
typedef struct { uint8_t len, wave; uint16_t f0, f1; uint8_t vol; } Sfx;

static const Sfx sfx_tab[] = {
    /* JUMP */ { 8, 0, 300, 620, 60 },
    /* AXE */ { 8, 1, 900, 200, 110 },
    /* HIT */ { 8, 1, 500, 160, 150 },
    /* HURT */ { 20, 0, 500, 90, 180 },
    /* RUSH */ { 14, 1, 300, 1400, 110 },
    /* HEAL */ { 24, 0, 400, 800, 70 },
    /* PICKUP */ { 36, 0, 440, 1320, 90 },
    /* SAVE */ { 22, 0, 880, 440, 90 },
    /* BLIP */ { 2, 0, 1000, 1000, 40 },
    /* ROAR */ { 44, 1, 200, 60, 200 },
    /* DIE */ { 44, 0, 800, 60, 170 },
    /* SLAM */ { 24, 1, 180, 40, 220 },
    /* KILL */ { 10, 1, 700, 120, 150 },
    /* SELECT */ { 6, 0, 800, 1000, 70 },
    /* LAND */ { 4, 1, 300, 150, 80 },
    /* HOOK */ { 12, 0, 1200, 500, 90 },
    /* BELL */ { 60, 0, 1046, 1040, 160 },
};

static Voice lead, bass;
static uint8_t song = 255, playing, tick_c, drum_t, beat;
static uint32_t noise = 0xACE1;
static uint32_t notes[60];
static struct { uint8_t on, id; uint16_t t; uint32_t phase; } sv[2];
static int samples_to_tick;
static uint32_t rate_step(uint32_t hz) { return (uint32_t)(((uint64_t)hz << 32) / AUDIO_RATE); }

static uint32_t note_hz_q8(int i) {
    /* C2 = 65.406 Hz, q8; twelfth root of two in q16 is 69433 */
    uint64_t v = 16744;
    int k;
    for (k = 0; k < i; k++) v = (v * 69433) >> 16;
    return (uint32_t)v;
}

void audio_reset(void) {
    int i;
    for (i = 0; i < 60; i++) notes[i] = (uint32_t)(((uint64_t)note_hz_q8(i) << 24) / AUDIO_RATE);
    playing = 0;
    song = 255;
    sv[0].on = sv[1].on = 0;
    samples_to_tick = 0;
}

void music_play(uint8_t s) {
    if (s == song && playing) return;
    song = s;
    lead.p = songs[s].lead; bass.p = songs[s].bass;
    lead.t = bass.t = 1;
    tick_c = songs[s].tick;
    beat = 0;
    playing = 1;
    G.song = s;
}

void music_stop(void) {
    playing = 0;
    song = 255;
    lead.note = bass.note = 0;
}

void sfx(uint8_t id) {
    int v = sfx_tab[id].wave == 1 ? 1 : 0;
    sv[v].on = 1; sv[v].id = id; sv[v].t = 0;
}

static void step_voice(Voice *v, const uint8_t *start) {
    if (--v->t == 0) {
        if (v->p[0] == 255) v->p = start;
        v->note = v->p[0];
        v->t = v->p[1];
        v->step = v->note ? notes[v->note - 1] : 0;
        v->env = 255;
        v->p += 2;
    }
}

static void tick60(void) {
    if (playing) {
        if (++tick_c >= songs[song].tick) {
            tick_c = 0;
            step_voice(&lead, songs[song].lead);
            step_voice(&bass, songs[song].bass);
            if (songs[song].drums) {
                if ((beat & 3) == 0) drum_t = 6;
                else if ((beat & 1) == 0) drum_t = 2;
                beat++;
            }
        }
        if (lead.env > 90) lead.env -= 3;
    }
    if (drum_t) drum_t--;
}

void audio_fill(int16_t *out, int n) {
    int i, k;
    static const uint8_t duty_lim[4] = { 32, 64, 128, 192 };
    for (i = 0; i < n; i++) {
        int32_t mix = 0;
        if (samples_to_tick-- <= 0) {
            samples_to_tick += AUDIO_RATE / TICK_HZ;
            tick60();
            for (k = 0; k < 2; k++)
                if (sv[k].on && ++sv[k].t >= sfx_tab[sv[k].id].len) sv[k].on = 0;
        }
        if (playing && lead.note) {
            lead.phase += lead.step;
            mix += ((lead.phase >> 24) < duty_lim[songs[song].duty] ? 1 : -1) * (lead.env * 14);
        }
        if (playing && bass.note) {
            int32_t t;
            bass.phase += bass.step;
            t = (int32_t)(bass.phase >> 24);
            t = t < 128 ? t * 2 - 128 : 383 - t * 2;
            mix += t * 22;
        }
        if (drum_t) {
            noise = (noise >> 1) ^ (-(int32_t)(noise & 1) & 0xB400u);
            mix += (noise & 1 ? 1 : -1) * 1500;
        }
        for (k = 0; k < 2; k++) {
            if (sv[k].on) {
                const Sfx *s = &sfx_tab[sv[k].id];
                uint32_t f = s->f0 + (int32_t)(s->f1 - s->f0) * (int32_t)sv[k].t / s->len;
                int32_t amp = s->vol * 40 * (s->len - sv[k].t) / s->len;
                if (s->wave == 0) {
                    sv[k].phase += rate_step(f);
                    mix += ((sv[k].phase >> 31) ? 1 : -1) * amp;
                } else {
                    sv[k].phase += rate_step(f);
                    if ((sv[k].phase >> 28) == 0) noise = (noise >> 1) ^ (-(int32_t)(noise & 1) & 0xB400u);
                    mix += (noise & 1 ? 1 : -1) * amp;
                }
            }
        }
        if (mix > 30000) mix = 30000;
        if (mix < -30000) mix = -30000;
        out[i] = (int16_t)mix;
    }
}
