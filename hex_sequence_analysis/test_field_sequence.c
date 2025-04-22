// hex_sequence_analysis/test_field_sequence.c
// Test harness to verify 5x52 field conversions against a known 160‑entry sequence

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Adjust these include paths to point at your secp256k1 field headers
#include "util.h"
#include "num.h"
#include "field.h"
#include "field_5x52_impl.h"

int main(void) {
    FILE *f = fopen("verified_bitcoin_sequence.txt", "r");
    if (!f) { perror("fopen"); return 1; }
    int idx;
    char hex[65], status[16];
    while (fscanf(f, "%d. %64s - %15s\n", &idx, hex, status) == 3) {
        unsigned char bin[32];
        for (int i = 0; i < 32; i++) {
            sscanf(hex + 2*i, "%2hhx", &bin[i]);
        }
        secp256k1_fe felem;
        if (!secp256k1_fe_set_b32(&felem, bin)) {
            printf("%3d: %s -> set_b32 failed\n", idx, hex);
            continue;
        }
        secp256k1_fe_normalize(&felem);
        unsigned char out[32];
        secp256k1_fe_get_b32(out, &felem);
        printf("%3d: %s -> ", idx, hex);
        for (int i = 0; i < 32; i++) printf("%02x", out[i]);
        printf(" [%s]\n", strcmp(hex, (const char *)out)==0 ? "OK" : "MISMATCH");
    }
    fclose(f);
    return 0;
} 