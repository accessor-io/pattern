#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/obj_mac.h> // For NID_secp256k1

// Structure to hold a point and its Pollard's Rho coefficients
typedef struct {
    EC_POINT *point;
    BIGNUM *a; // Coefficient for G
    BIGNUM *b; // Coefficient for P (public key)
} PollardPointState;

// Function prototypes will go here
PollardPointState* pollard_point_state_new(const EC_GROUP *group, BN_CTX *ctx);
void pollard_point_state_free(PollardPointState *state);
int parse_public_key(const EC_GROUP *group, EC_POINT *pub_key_point, const char *hex_pub_key, BN_CTX *ctx);
void pollard_rho_iteration(const EC_GROUP *group, PollardPointState *current_state, const EC_POINT *G, const EC_POINT *P_key, const BIGNUM *order, BN_CTX *ctx);

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <public_key_hex>\\n", argv[0]);
        fprintf(stderr, "Example: %s 0479BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8\\n", argv[0]);
        return 1;
    }
    char *pub_key_hex = argv[1];

    printf("Pollard's Rho ECDLP Solver (secp256k1)\\n");

    // Initialize secp256k1 curve
    EC_GROUP *group = EC_GROUP_new_by_curve_name(NID_secp256k1);
    if (!group) {
        fprintf(stderr, "Error creating EC_GROUP object\\n");
        return 1;
    }

    const BIGNUM *order = EC_GROUP_get0_order(group);
    BN_CTX *ctx = BN_CTX_new();
    if (!ctx) {
        fprintf(stderr, "Error creating BN_CTX object\\n");
        EC_GROUP_free(group);
        return 1;
    }

    // Define Generator G for secp256k1
    EC_POINT *G = EC_POINT_dup(EC_GROUP_get0_generator(group), group);
    if (!G) {
        fprintf(stderr, "Error getting generator point G\\n");
        BN_CTX_free(ctx);
        EC_GROUP_free(group);
        return 1;
    }
    print_point_bn(group, G, ctx, "Generator G:");

    // Define Public Key P (target point) from command line argument
    EC_POINT *P_key = EC_POINT_new(group);
    if (!P_key) {
        fprintf(stderr, "Error creating EC_POINT for public key P\\n");
        EC_POINT_free(G);
        BN_CTX_free(ctx);
        EC_GROUP_free(group);
        return 1;
    }
    if (!parse_public_key(group, P_key, pub_key_hex, ctx)) {
        fprintf(stderr, "Error parsing public key from hex string.\\n");
        EC_POINT_free(P_key);
        EC_POINT_free(G);
        BN_CTX_free(ctx);
        EC_GROUP_free(group);
        return 1;
    }
    print_point_bn(group, P_key, ctx, "Public Key P:");

    // Initialize Tortoise and Hare states
    PollardPointState *tortoise_state = pollard_point_state_new(group, ctx);
    PollardPointState *hare_state = pollard_point_state_new(group, ctx);

    if (!tortoise_state || !hare_state) {
        fprintf(stderr, "Failed to initialize tortoise/hare states\\n");
        if (tortoise_state) pollard_point_state_free(tortoise_state);
        if (hare_state) pollard_point_state_free(hare_state);
        EC_POINT_free(P_key);
        EC_POINT_free(G);
        BN_CTX_free(ctx);
        EC_GROUP_free(group);
        return 1;
    }

    // Initial state: X0 = G, a0 = 1, b0 = 0
    // (Alternatively, start with P, or a random point kG + lP)
    EC_POINT_copy(tortoise_state->point, G);
    BN_one(tortoise_state->a);
    BN_zero(tortoise_state->b);

    EC_POINT_copy(hare_state->point, G);
    BN_one(hare_state->a);
    BN_zero(hare_state->b);

    printf("Starting Pollard's Rho search...\\n");
    unsigned long iterations = 0;
    const unsigned long max_iterations = 10000000; // Safeguard

    while(iterations < max_iterations) {
        iterations++;

        // Tortoise: X_t = f(X_t)
        pollard_rho_iteration(group, tortoise_state, G, P_key, order, ctx);

        // Hare: X_h = f(f(X_h))
        pollard_rho_iteration(group, hare_state, G, P_key, order, ctx);
        pollard_rho_iteration(group, hare_state, G, P_key, order, ctx);

        if (EC_POINT_cmp(group, tortoise_state->point, hare_state->point, ctx) == 0) {
            printf("Collision found after %lu iterations!\\n", iterations);
            print_point_bn(group, tortoise_state->point, ctx, "Collision Point (Tortoise):");
            printf("Tortoise (a1, b1): ("); BN_print_fp(stdout, tortoise_state->a); printf(", "); BN_print_fp(stdout, tortoise_state->b); printf(")\\n");
            print_point_bn(group, hare_state->point, ctx, "Collision Point (Hare):");
            printf("Hare (a2, b2): ("); BN_print_fp(stdout, hare_state->a); printf(", "); BN_print_fp(stdout, hare_state->b); printf(")\\n");

            // Calculate k = (a1 - a2) * (b2 - b1)^-1 mod order
            BIGNUM *a_diff = BN_new(); // a1 - a2
            BIGNUM *b_diff_inv = BN_new(); // (b2 - b1)^-1
            BIGNUM *b_diff_val = BN_new(); // b2 - b1
            BIGNUM *private_key_k = BN_new();

            if (!a_diff || !b_diff_inv || !b_diff_val || !private_key_k) {
                fprintf(stderr, "BN allocation failed for final calculation\\n");
                // Free allocated BNs
                break;
            }

            // a_diff = tortoise_state->a - hare_state->a  (a1 - a2)
            if (!BN_mod_sub(a_diff, tortoise_state->a, hare_state->a, order, ctx)) {
                 fprintf(stderr, "BN_mod_sub for a_diff failed.\\n"); break;
            }

            // b_diff_val = hare_state->b - tortoise_state->b (b2 - b1)
            if (!BN_mod_sub(b_diff_val, hare_state->b, tortoise_state->b, order, ctx)) {
                fprintf(stderr, "BN_mod_sub for b_diff_val failed.\\n"); break;
            }

            if (BN_is_zero(b_diff_val)) {
                fprintf(stderr, "Error: (b2 - b1) is zero. Cannot compute inverse. Try different start or parameters.\\n");
                // This indicates a failure specific to this run, possibly needing a restart with different random choices
                // or a different iteration function if it leads to trivial cycles.
                // Free allocated BNs
                break;
            }

            // b_diff_inv = (b_diff_val)^-1 mod order
            if (!BN_mod_inverse(b_diff_inv, b_diff_val, order, ctx)) {
                fprintf(stderr, "Error: Failed to compute modular inverse of (b2 - b1). It might be non-invertible (gcd != 1 with order).\\n");
                //ERR_print_errors_fp(stderr);
                // Free allocated BNs
                break;
            }

            // private_key_k = a_diff * b_diff_inv mod order
            if (!BN_mod_mul(private_key_k, a_diff, b_diff_inv, order, ctx)) {
                fprintf(stderr, "BN_mod_mul for private_key_k failed.\\n"); break;
            }

            printf("Calculated Private Key (k): ");
            BN_print_fp(stdout, private_key_k);
            printf("\\n");
            
            // Verification: P_key_check = private_key_k * G
            EC_POINT *P_key_check = EC_POINT_new(group);
            if (P_key_check && EC_POINT_mul(group, P_key_check, private_key_k, NULL, NULL, ctx)) {
                print_point_bn(group, P_key_check, ctx, "Verification (k*G):");
                if (EC_POINT_cmp(group, P_key, P_key_check, ctx) == 0) {
                    printf("SUCCESS: Verification k*G == P_key matches!\\n");
                } else {
                    printf("ERROR: Verification k*G != P_key. Something went wrong.\\n");
                }
            } else {
                 fprintf(stderr, "Error during verification step.\\n");
            }
            if(P_key_check) EC_POINT_free(P_key_check);

            BN_free(a_diff);
            BN_free(b_diff_inv);
            BN_free(b_diff_val);
            BN_free(private_key_k);
            break; // Exit loop after finding solution
        }

        if (iterations % 100000 == 0) { // Print progress
            BIGNUM *tx = BN_new(); BIGNUM *hx = BN_new();
            char *tx_hex = NULL; char *hx_hex = NULL;
            if (tx && EC_POINT_get_affine_coordinates_GFp(group, tortoise_state->point, tx, NULL, ctx)) {
                tx_hex = BN_bn2hex(tx);
            }
            if (hx && EC_POINT_get_affine_coordinates_GFp(group, hare_state->point, hx, NULL, ctx)) {
                hx_hex = BN_bn2hex(hx);
            }
            printf("Iterations: %lu (Tortoise X: %s, Hare X: %s)\\n", 
                   iterations, 
                   tx_hex ? tx_hex : "(inf)", 
                   hx_hex ? hx_hex : "(inf)");
            if (tx) BN_free(tx); if (hx) BN_free(hx);
            if (tx_hex) OPENSSL_free(tx_hex);
            if (hx_hex) OPENSSL_free(hx_hex);
        }
    }

    if (iterations == max_iterations) {
        printf("Max iterations reached without finding a collision.\\n");
    }

    // Cleanup for tortoise and hare states
    pollard_point_state_free(tortoise_state);
    pollard_point_state_free(hare_state);

    // TODO:
    // 5. Calculate the discrete logarithm (Done as part of collision handling)
    printf("\\n");

    // Cleanup
    EC_POINT_free(P_key);
    EC_POINT_free(G);
    BN_CTX_free(ctx);
    EC_GROUP_free(group);

    return 0;
}

// Helper function to print a point (for debugging)
void print_point_bn(const EC_GROUP *group, const EC_POINT *point, BN_CTX *ctx, const char *label) {
    BIGNUM *x = BN_new();
    BIGNUM *y = BN_new();
    if (EC_POINT_get_affine_coordinates_GFp(group, point, x, y, ctx)) {
        printf("%s (X: ", label);
        BN_print_fp(stdout, x);
        printf(", Y: ");
        BN_print_fp(stdout, y);
        printf(")\\n");
    } else {
        fprintf(stderr, "Error getting affine coordinates for %s\\n", label);
    }
    BN_free(x);
    BN_free(y);
}

PollardPointState* pollard_point_state_new(const EC_GROUP *group, BN_CTX *ctx) {
    PollardPointState *state = (PollardPointState*)malloc(sizeof(PollardPointState));
    if (!state) {
        fprintf(stderr, "Failed to allocate PollardPointState\\n");
        return NULL;
    }
    state->point = EC_POINT_new(group);
    state->a = BN_new();
    state->b = BN_new();
    if (!state->point || !state->a || !state->b) {
        fprintf(stderr, "Failed to allocate members of PollardPointState\\n");
        if (state->point) EC_POINT_free(state->point);
        if (state->a) BN_free(state->a);
        if (state->b) BN_free(state->b);
        free(state);
        return NULL;
    }
    BN_zero(state->a);
    BN_zero(state->b);
    return state;
}

void pollard_point_state_free(PollardPointState *state) {
    if (state) {
        if (state->point) EC_POINT_free(state->point);
        if (state->a) BN_free(state->a);
        if (state->b) BN_free(state->b);
        free(state);
    }
}

// Function to parse a public key from a hex string (e.g., "04X_hexY_hex")
int parse_public_key(const EC_GROUP *group, EC_POINT *pub_key_point, const char *hex_pub_key, BN_CTX *ctx) {
    if (EC_POINT_hex2point(group, hex_pub_key, pub_key_point, ctx) == NULL) {
        fprintf(stderr, "EC_POINT_hex2point failed for public key: %s\\n", hex_pub_key);
        //ERR_print_errors_fp(stderr); // For more detailed OpenSSL errors
        return 0; // Failure
    }
    // Check if the point is on the curve
    if (!EC_POINT_is_on_curve(group, pub_key_point, ctx)) {
        fprintf(stderr, "Parsed public key is not on the curve!\\n");
        return 0; // Failure
    }
    return 1; // Success
}

// Pollard's Rho iteration function f(X, a, b)
// Updates current_state->point, current_state->a, current_state->b
void pollard_rho_iteration(const EC_GROUP *group, PollardPointState *current_state, 
                           const EC_POINT *G_point, const EC_POINT *P_key_point, 
                           const BIGNUM *order, BN_CTX *ctx) {
    BIGNUM *x_coord = BN_new();
    if (!x_coord) {
        fprintf(stderr, "Failed to allocate BIGNUM for x_coord in iteration\\n");
        return; // Or handle error more gracefully
    }

    // Get x-coordinate of the current point in the state
    if (EC_POINT_is_at_infinity(group, current_state->point)) {
        // This case should ideally not be hit often if P is not the point at infinity
        // Or if the iteration starts with a valid point. Handle as a reset or specific rule.
        // For now, let's add G if it's infinity (arbitrary choice, can be refined)
        // This also means the point was likely (0,0) if a,b were 0
        EC_POINT_copy(current_state->point, G_point);
        BN_one(current_state->a); // a = 1
        BN_zero(current_state->b); // b = 0
        BN_mod(current_state->a, current_state->a, order, ctx); // a = a mod n
        BN_mod(current_state->b, current_state->b, order, ctx); // b = b mod n
        BN_free(x_coord);
        return;
    }

    if (!EC_POINT_get_affine_coordinates_GFp(group, current_state->point, x_coord, NULL, ctx)) {
        fprintf(stderr, "Failed to get x-coordinate in iteration\\n");
        // Handle error: maybe try to double the point or add G/P?
        // For now, just return to avoid crashing.
        BN_free(x_coord);
        return;
    }

    unsigned long x_mod_3 = BN_mod_word(x_coord, 3);

    if (x_mod_3 == 0) { // Group 0: X_new = X_old + G_point
        if (!EC_POINT_add(group, current_state->point, current_state->point, G_point, ctx)) {
            fprintf(stderr, "EC_POINT_add failed for X+G\\n"); return;
        }
        if (!BN_mod_add(current_state->a, current_state->a, BN_value_one(), order, ctx)) {
            fprintf(stderr, "BN_mod_add failed for a+1\\n"); return;
        }
        // b remains current_state->b, ensure it's mod order (though it should be already)
        // BN_mod(current_state->b, current_state->b, order, ctx);
    } else if (x_mod_3 == 1) { // Group 1: X_new = X_old + P_key_point
        if (!EC_POINT_add(group, current_state->point, current_state->point, P_key_point, ctx)) {
            fprintf(stderr, "EC_POINT_add failed for X+P\\n"); return;
        }
        if (!BN_mod_add(current_state->b, current_state->b, BN_value_one(), order, ctx)) {
            fprintf(stderr, "BN_mod_add failed for b+1\\n"); return;
        }
        // a remains current_state->a
        // BN_mod(current_state->a, current_state->a, order, ctx);
    } else { // Group 2 (x_mod_3 == 2): X_new = 2 * X_old
        if (!EC_POINT_dbl(group, current_state->point, current_state->point, ctx)) {
            fprintf(stderr, "EC_POINT_dbl failed for 2X\\n"); return;
        }
        if (!BN_mod_add(current_state->a, current_state->a, current_state->a, order, ctx)) { // a = 2a mod n
            fprintf(stderr, "BN_mod_add failed for 2a\\n"); return;
        }
        if (!BN_mod_add(current_state->b, current_state->b, current_state->b, order, ctx)) { // b = 2b mod n
            fprintf(stderr, "BN_mod_add failed for 2b\\n"); return;
        }
    }

    BN_free(x_coord);
} 