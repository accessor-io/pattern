#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/ripemd.h>
#include <openssl/ec.h>
#include <openssl/obj_mac.h>
#include <openssl/bn.h>
#include <time.h>

#define STEP_SIZE 100
#define REPORT_INTERVAL 1000

// Base58 character set
const char *BASE58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

// Hash wrapper functions for newer OpenSSL
void sha256_hash(const unsigned char *input, size_t length, unsigned char *output) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_sha256(), NULL);
    EVP_DigestUpdate(ctx, input, length);
    EVP_DigestFinal_ex(ctx, output, NULL);
    EVP_MD_CTX_free(ctx);
}

void ripemd160_hash(const unsigned char *input, size_t length, unsigned char *output) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_ripemd160(), NULL);
    EVP_DigestUpdate(ctx, input, length);
    EVP_DigestFinal_ex(ctx, output, NULL);
    EVP_MD_CTX_free(ctx);
}

// Pad a hex string with leading zeros to a total length of 64 characters
char* pad_hex_key(const char* short_key_in) {
    const char* short_key = short_key_in;
    if (strncmp(short_key, "0x", 2) == 0 || strncmp(short_key, "0X", 2) == 0) {
        short_key += 2; // Skip the "0x" or "0X" prefix
    }

    size_t short_len = strlen(short_key);
    if (short_len >= 64) {
        char* dup_key = strdup(short_key);
        if (!dup_key) fprintf(stderr, "Memory allocation failed for duplicating key\n");
        return dup_key;
    }
    char* padded_key = (char*)malloc(65); // 64 chars + null terminator
    if (!padded_key) {
        fprintf(stderr, "Memory allocation failed for padding key\n");
        return NULL;
    }
    memset(padded_key, '0', 64 - short_len);
    strcpy(padded_key + (64 - short_len), short_key);
    padded_key[64] = '\0';
    return padded_key;
}

// Convert bytes to base58check
char *base58check_encode(const unsigned char *input, size_t length) {
    unsigned char extended[length + 1];
    extended[0] = 0x00;  // mainnet address
    memcpy(extended + 1, input, length);
    
    unsigned char hash1[32];
    unsigned char hash2[32];
    sha256_hash(extended, length + 1, hash1);
    sha256_hash(hash1, 32, hash2);
    
    unsigned char final[length + 5];
    memcpy(final, extended, length + 1);
    memcpy(final + length + 1, hash2, 4);
    
    char *result = calloc(50, sizeof(char));
    if (!result) { fprintf(stderr, "Failed to allocate memory for base58 result\n"); return NULL; }

    BIGNUM *bn = BN_new();
    BIGNUM *bn58 = BN_new();
    BIGNUM *rem = BN_new();
    BN_CTX *ctx_bn = BN_CTX_new(); // Renamed to avoid conflict with outer scope ctx

    if (!bn || !bn58 || !rem || !ctx_bn) {
        fprintf(stderr, "Failed to create BIGNUM or BN_CTX objects for base58 encoding\n");
        if (result) free(result);
        if (bn) BN_free(bn);
        if (bn58) BN_free(bn58);
        if (rem) BN_free(rem);
        if (ctx_bn) BN_CTX_free(ctx_bn);
        return NULL;
    }
    
    BN_bin2bn(final, length + 5, bn);
    BN_set_word(bn58, 58);
    
    size_t leading_zeros = 0;
    for (size_t i = 0; i < length + 5 && final[i] == 0; i++) {
        leading_zeros++;
    }
    
    int pos = 0;
    while (!BN_is_zero(bn)) {
        if (!BN_div(bn, rem, bn, bn58, ctx_bn)) {
            fprintf(stderr, "BN_div failed in base58 encoding\n");
            free(result);
            BN_free(bn);
            BN_free(bn58);
            BN_free(rem);
            BN_CTX_free(ctx_bn);
            return NULL;
        }
        result[pos++] = BASE58_CHARS[BN_get_word(rem)];
    }
    
    for (size_t i = 0; i < leading_zeros; i++) {
        result[pos++] = '1';
    }
    result[pos] = '\0';
    
    int len = strlen(result);
    for (int i = 0; i < len / 2; i++) {
        char temp = result[i];
        result[i] = result[len - 1 - i];
        result[len - 1 - i] = temp;
    }
    
    BN_free(bn);
    BN_free(bn58);
    BN_free(rem);
    BN_CTX_free(ctx_bn);
    
    return result;
}

int main() {
    const char *input_key_with_prefix = "0491b84b6431a6c4ef2";
    char *private_key_hex = pad_hex_key(input_key_with_prefix);

    if (!private_key_hex) {
        return 1;
    }

    printf("\nBitcoin Private Key to Address Converter\n");
    printf("========================================\n");
    printf("Input Private Key:    %s\n", input_key_with_prefix);
    printf("Padded Private Key:   %s\n", private_key_hex);

    BIGNUM *priv_bn = BN_new();
    if (!priv_bn || !BN_hex2bn(&priv_bn, private_key_hex)) {
        fprintf(stderr, "Failed to convert private key hex '%s' to BIGNUM\n", private_key_hex);
        free(private_key_hex);
        if (priv_bn) BN_free(priv_bn);
        return 1;
    }

    EC_GROUP *group = EC_GROUP_new_by_curve_name(NID_secp256k1);
    EC_POINT *pub_point = EC_POINT_new(group);
    BN_CTX *ctx = BN_CTX_new(); // This is for EC_POINT_mul

    if (!group || !pub_point || !ctx) {
        fprintf(stderr, "Failed to initialize curve objects\n");
        free(private_key_hex);
        BN_free(priv_bn);
        if (group) EC_GROUP_free(group);
        if (pub_point) EC_POINT_free(pub_point);
        if (ctx) BN_CTX_free(ctx);
        return 1;
    }

    if (!EC_POINT_mul(group, pub_point, priv_bn, NULL, NULL, ctx)) {
        fprintf(stderr, "Failed to compute public key point\n");
        free(private_key_hex);
        BN_free(priv_bn);
        EC_GROUP_free(group);
        EC_POINT_free(pub_point);
        BN_CTX_free(ctx);
        return 1;
    }

    unsigned char pub_key_compressed[33];
    size_t pub_len = EC_POINT_point2oct(group, pub_point, POINT_CONVERSION_COMPRESSED,
                                      pub_key_compressed, sizeof(pub_key_compressed), ctx);
    if (pub_len == 0) {
        fprintf(stderr, "Failed to convert public key point to octet string\n");
        free(private_key_hex);
        BN_free(priv_bn);
        EC_GROUP_free(group);
        EC_POINT_free(pub_point);
        BN_CTX_free(ctx);
        return 1;
    }

    unsigned char hash_digest[32];
    unsigned char ripemd_digest[20];
    sha256_hash(pub_key_compressed, pub_len, hash_digest);
    ripemd160_hash(hash_digest, 32, ripemd_digest);

    char *address = base58check_encode(ripemd_digest, 20);
    if (!address) {
         fprintf(stderr, "Failed to encode address\n");
        free(private_key_hex);
        BN_free(priv_bn);
        EC_GROUP_free(group);
        EC_POINT_free(pub_point);
        BN_CTX_free(ctx);
        return 1;
    }

    printf("Bitcoin Address:      %s\n", address);
    printf("========================================\n\n");

    // Cleanup
    free(private_key_hex);
    BN_free(priv_bn);
    EC_GROUP_free(group);
    EC_POINT_free(pub_point);
    BN_CTX_free(ctx);
    free(address);

    return 0;
} 