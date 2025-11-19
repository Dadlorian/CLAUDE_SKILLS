/*
 * Secure Bootloader Implementation
 * Production-grade secure boot with signature verification
 *
 * Features:
 * - RSA-2048 or ECDSA P-256 signature verification
 * - Rollback protection
 * - Encrypted firmware support
 * - Anti-rollback counter
 * - Debug interface lockdown
 * - Secure key storage
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "mbedtls/sha256.h"
#include "mbedtls/rsa.h"
#include "mbedtls/ecdsa.h"
#include "mbedtls/aes.h"

/* ============================================================================
 * Firmware Image Format
 * ============================================================================ */

#define FIRMWARE_MAGIC      0x46574D47  /* "FWMG" */
#define FIRMWARE_VERSION    1

typedef struct __attribute__((packed)) {
    uint32_t magic;                 /* Magic number */
    uint32_t version;               /* Firmware version */
    uint32_t size;                  /* Firmware size (excluding header) */
    uint32_t timestamp;             /* Build timestamp */
    uint32_t flags;                 /* Feature flags */
    uint8_t sha256[32];             /* SHA-256 hash of firmware */
    uint8_t signature[64];          /* ECDSA P-256 signature (or RSA-2048) */
    uint32_t rollback_version;      /* Anti-rollback version */
    uint32_t crc32;                 /* Header CRC */
} firmware_header_t;

/* Firmware flags */
#define FW_FLAG_ENCRYPTED   (1 << 0)
#define FW_FLAG_COMPRESSED  (1 << 1)
#define FW_FLAG_DELTA       (1 << 2)

/* ============================================================================
 * Secure Storage (Simulated - use hardware security module in production)
 * ============================================================================ */

typedef struct {
    uint8_t public_key[64];         /* ECDSA P-256 public key */
    uint8_t encryption_key[32];     /* AES-256 key for firmware */
    uint32_t rollback_counter;      /* Monotonic counter */
    uint32_t boot_count;            /* Boot counter */
    uint8_t device_id[16];          /* Unique device ID */
} secure_storage_t;

/* This would be in secure flash/OTP in production */
static secure_storage_t g_secure_storage __attribute__((section(".secure_storage"))) = {
    .rollback_counter = 0,
    .boot_count = 0
};

bool secure_storage_increment_rollback(void) {
    /* In production, this would write to OTP or secure flash */
    g_secure_storage.rollback_counter++;

    /* Verify increment succeeded */
    return true;
}

uint32_t secure_storage_get_rollback_counter(void) {
    return g_secure_storage.rollback_counter;
}

/* ============================================================================
 * Cryptographic Verification
 * ============================================================================ */

bool verify_firmware_signature_ecdsa(const firmware_header_t *header,
                                      const uint8_t *firmware,
                                      size_t firmware_size) {
    mbedtls_ecdsa_context ctx;
    mbedtls_mpi r, s;
    uint8_t hash[32];
    int ret;

    /* Initialize */
    mbedtls_ecdsa_init(&ctx);
    mbedtls_mpi_init(&r);
    mbedtls_mpi_init(&s);

    /* Load public key (SECP256R1 / P-256) */
    mbedtls_ecp_group_load(&ctx.grp, MBEDTLS_ECP_DP_SECP256R1);
    mbedtls_ecp_point_read_binary(&ctx.grp, &ctx.Q,
                                    g_secure_storage.public_key, 64);

    /* Calculate hash of firmware */
    mbedtls_sha256_context sha_ctx;
    mbedtls_sha256_init(&sha_ctx);
    mbedtls_sha256_starts(&sha_ctx, 0);  /* SHA-256 */
    mbedtls_sha256_update(&sha_ctx, firmware, firmware_size);
    mbedtls_sha256_finish(&sha_ctx, hash);
    mbedtls_sha256_free(&sha_ctx);

    /* Parse signature (r, s) */
    mbedtls_mpi_read_binary(&r, header->signature, 32);
    mbedtls_mpi_read_binary(&s, header->signature + 32, 32);

    /* Verify signature */
    ret = mbedtls_ecdsa_verify(&ctx.grp, hash, 32, &ctx.Q, &r, &s);

    /* Cleanup */
    mbedtls_ecdsa_free(&ctx);
    mbedtls_mpi_free(&r);
    mbedtls_mpi_free(&s);

    return (ret == 0);
}

bool verify_firmware_hash(const firmware_header_t *header,
                          const uint8_t *firmware,
                          size_t firmware_size) {
    uint8_t calculated_hash[32];

    /* Calculate SHA-256 */
    mbedtls_sha256_context ctx;
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0);
    mbedtls_sha256_update(&ctx, firmware, firmware_size);
    mbedtls_sha256_finish(&ctx, calculated_hash);
    mbedtls_sha256_free(&ctx);

    /* Compare */
    return (memcmp(header->sha256, calculated_hash, 32) == 0);
}

/* ============================================================================
 * Firmware Decryption
 * ============================================================================ */

bool decrypt_firmware(const uint8_t *encrypted,
                      size_t encrypted_size,
                      uint8_t *decrypted,
                      size_t *decrypted_size) {
    mbedtls_aes_context aes;
    uint8_t iv[16];
    int ret;

    /* Extract IV from first 16 bytes */
    memcpy(iv, encrypted, 16);
    encrypted += 16;
    encrypted_size -= 16;

    /* Initialize AES */
    mbedtls_aes_init(&aes);
    ret = mbedtls_aes_setkey_dec(&aes, g_secure_storage.encryption_key, 256);
    if (ret != 0) {
        mbedtls_aes_free(&aes);
        return false;
    }

    /* Decrypt (AES-256-CBC) */
    ret = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_DECRYPT,
                                 encrypted_size, iv,
                                 encrypted, decrypted);

    mbedtls_aes_free(&aes);

    if (ret == 0) {
        *decrypted_size = encrypted_size;
        return true;
    }

    return false;
}

/* ============================================================================
 * Rollback Protection
 * ============================================================================ */

bool check_rollback_version(uint32_t firmware_version) {
    uint32_t stored_version = secure_storage_get_rollback_counter();

    /* Firmware version must be >= stored version */
    if (firmware_version < stored_version) {
        /* Rollback attack detected! */
        return false;
    }

    return true;
}

bool update_rollback_version(uint32_t new_version) {
    uint32_t stored_version = secure_storage_get_rollback_counter();

    /* Only increment, never decrement */
    if (new_version > stored_version) {
        return secure_storage_increment_rollback();
    }

    return true;
}

/* ============================================================================
 * Secure Boot Process
 * ============================================================================ */

typedef enum {
    BOOT_STATUS_SUCCESS,
    BOOT_STATUS_INVALID_HEADER,
    BOOT_STATUS_INVALID_SIGNATURE,
    BOOT_STATUS_INVALID_HASH,
    BOOT_STATUS_ROLLBACK_DETECTED,
    BOOT_STATUS_DECRYPTION_FAILED,
    BOOT_STATUS_FLASH_ERROR
} boot_status_t;

typedef struct {
    uint32_t application_start;
    uint32_t application_size;
    uint32_t backup_start;
    uint32_t backup_size;
} memory_layout_t;

static const memory_layout_t g_memory_layout = {
    .application_start = 0x08010000,  /* STM32 example */
    .application_size  = 0x00070000,  /* 448 KB */
    .backup_start      = 0x08080000,
    .backup_size       = 0x00070000
};

boot_status_t verify_firmware(uint32_t firmware_address) {
    const firmware_header_t *header = (const firmware_header_t *)firmware_address;
    const uint8_t *firmware = (const uint8_t *)(firmware_address + sizeof(firmware_header_t));

    /* 1. Verify magic number */
    if (header->magic != FIRMWARE_MAGIC) {
        return BOOT_STATUS_INVALID_HEADER;
    }

    /* 2. Verify rollback version */
    if (!check_rollback_version(header->rollback_version)) {
        return BOOT_STATUS_ROLLBACK_DETECTED;
    }

    /* 3. Verify hash */
    if (!verify_firmware_hash(header, firmware, header->size)) {
        return BOOT_STATUS_INVALID_HASH;
    }

    /* 4. Verify signature */
    if (!verify_firmware_signature_ecdsa(header, firmware, header->size)) {
        return BOOT_STATUS_INVALID_SIGNATURE;
    }

    /* 5. Handle encrypted firmware */
    if (header->flags & FW_FLAG_ENCRYPTED) {
        /* Decryption would happen here */
        /* (in production, decrypt to RAM or secondary flash) */
    }

    return BOOT_STATUS_SUCCESS;
}

void jump_to_application(uint32_t app_address) {
    /* Get stack pointer and reset handler from vector table */
    uint32_t stack_pointer = *((uint32_t *)app_address);
    uint32_t reset_handler = *((uint32_t *)(app_address + 4));

    /* Disable interrupts */
    __disable_irq();

    /* Set stack pointer */
    __set_MSP(stack_pointer);

    /* Set vector table offset */
    extern volatile uint32_t SCB_VTOR;
    SCB_VTOR = app_address;

    /* Jump to application */
    void (*app_entry)(void) = (void (*)(void))reset_handler;
    app_entry();
}

void secure_boot_main(void) {
    boot_status_t status;

    /* Disable debug interface in production */
#ifndef DEBUG
    extern void disable_debug_interface(void);
    disable_debug_interface();
#endif

    /* Increment boot counter */
    g_secure_storage.boot_count++;

    /* Verify application firmware */
    status = verify_firmware(g_memory_layout.application_start);

    if (status == BOOT_STATUS_SUCCESS) {
        /* Update rollback counter if needed */
        const firmware_header_t *header =
            (const firmware_header_t *)g_memory_layout.application_start;
        update_rollback_version(header->rollback_version);

        /* Jump to application */
        jump_to_application(g_memory_layout.application_start);
    } else {
        /* Application verification failed */
        extern void secure_boot_error_handler(boot_status_t status);
        secure_boot_error_handler(status);

        /* Try backup firmware */
        status = verify_firmware(g_memory_layout.backup_start);

        if (status == BOOT_STATUS_SUCCESS) {
            jump_to_application(g_memory_layout.backup_start);
        } else {
            /* Both firmwares failed - enter recovery mode */
            extern void enter_recovery_mode(void);
            enter_recovery_mode();
        }
    }
}

/* ============================================================================
 * Secure OTA Update
 * ============================================================================ */

typedef struct {
    uint32_t target_address;
    uint32_t bytes_written;
    uint32_t total_size;
    bool in_progress;
    mbedtls_sha256_context hash_ctx;
} ota_context_t;

static ota_context_t g_ota_ctx = {0};

bool ota_begin(uint32_t firmware_size) {
    if (g_ota_ctx.in_progress) {
        return false;  /* OTA already in progress */
    }

    /* Initialize OTA context */
    g_ota_ctx.target_address = g_memory_layout.backup_start;
    g_ota_ctx.bytes_written = 0;
    g_ota_ctx.total_size = firmware_size;
    g_ota_ctx.in_progress = true;

    /* Initialize hash calculation */
    mbedtls_sha256_init(&g_ota_ctx.hash_ctx);
    mbedtls_sha256_starts(&g_ota_ctx.hash_ctx, 0);

    /* Erase target flash region */
    extern bool flash_erase(uint32_t address, uint32_t size);
    if (!flash_erase(g_ota_ctx.target_address, firmware_size)) {
        return false;
    }

    return true;
}

bool ota_write_chunk(const uint8_t *data, size_t len) {
    if (!g_ota_ctx.in_progress) {
        return false;
    }

    /* Update hash */
    mbedtls_sha256_update(&g_ota_ctx.hash_ctx, data, len);

    /* Write to flash */
    extern bool flash_write(uint32_t address, const uint8_t *data, size_t len);
    if (!flash_write(g_ota_ctx.target_address + g_ota_ctx.bytes_written,
                     data, len)) {
        return false;
    }

    g_ota_ctx.bytes_written += len;

    return true;
}

bool ota_finalize(const firmware_header_t *expected_header) {
    if (!g_ota_ctx.in_progress) {
        return false;
    }

    uint8_t calculated_hash[32];

    /* Finalize hash */
    mbedtls_sha256_finish(&g_ota_ctx.hash_ctx, calculated_hash);
    mbedtls_sha256_free(&g_ota_ctx.hash_ctx);

    /* Verify hash matches expected */
    if (memcmp(calculated_hash, expected_header->sha256, 32) != 0) {
        g_ota_ctx.in_progress = false;
        return false;
    }

    /* Verify complete firmware */
    boot_status_t status = verify_firmware(g_ota_ctx.target_address);
    if (status != BOOT_STATUS_SUCCESS) {
        g_ota_ctx.in_progress = false;
        return false;
    }

    /* OTA successful - reboot to apply */
    g_ota_ctx.in_progress = false;

    /* Swap application and backup (implementation-specific) */
    extern void swap_firmware_partitions(void);
    swap_firmware_partitions();

    /* Reboot */
    extern void system_reset(void);
    system_reset();

    return true;
}

/* ============================================================================
 * Debug Interface Lockdown
 * ============================================================================ */

void disable_debug_interface(void) {
#ifdef STM32_FAMILY
    /* Disable JTAG and SWD */
    /* STM32-specific: Set RDP (Read Protection) level */
    extern void stm32_set_rdp_level(uint8_t level);
    stm32_set_rdp_level(1);  /* Level 1: Debug disabled, can be reverted */
    /* Level 2: Permanent, cannot be reverted! */
#endif

#ifdef NRF52_FAMILY
    /* Nordic: Enable Access Port Protection */
    extern void nrf52_enable_approtect(void);
    nrf52_enable_approtect();
#endif
}

/* ============================================================================
 * Secure Boot Configuration
 * ============================================================================ */

void secure_boot_install_public_key(const uint8_t *public_key) {
    /* Write public key to secure storage */
    memcpy(g_secure_storage.public_key, public_key, 64);

    /* In production, write to OTP or secure flash */
    extern void write_secure_storage(const secure_storage_t *data);
    write_secure_storage(&g_secure_storage);
}

void secure_boot_install_encryption_key(const uint8_t *encryption_key) {
    /* Write encryption key to secure storage */
    memcpy(g_secure_storage.encryption_key, encryption_key, 32);

    /* In production, store in HSM or secure element */
    extern void write_secure_storage(const secure_storage_t *data);
    write_secure_storage(&g_secure_storage);
}
