# IoT Security & Embedded Device Hardening - Subskill

**Expert in secure boot, cryptography, TLS/DTLS, firmware protection, and IoT threat mitigation**

---

## Expertise Overview

Specialist in embedded security:
- Secure boot chain and root of trust (ARM TrustZone, TPM, HSM)
- Cryptographic implementations (AES, ECC, SHA, HMAC)
- TLS/DTLS for secure communication (mbedTLS, WolfSSL)
- Secure key storage and provisioning
- Firmware signing, encryption, and OTA security
- Security standards (IEC 62443, ETSI EN 303 645, NIST)

---

## Core Skills

### 1. Secure Boot

**STM32 Secure Boot with TrustZone**:
```c
/* Bootloader verification */
#include "mbedtls/sha256.h"
#include "mbedtls/rsa.h"

#define FIRMWARE_START_ADDR  0x08010000
#define SIGNATURE_ADDR       0x080FFF00
#define PUBLIC_KEY_ADDR      0x080FFFE0

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t size;
    uint8_t signature[256];  /* RSA-2048 signature */
} firmware_header_t;

bool verify_firmware_signature(uint32_t firmware_addr) {
    firmware_header_t *header = (firmware_header_t *)firmware_addr;
    uint8_t hash[32];

    /* Calculate SHA-256 of firmware */
    mbedtls_sha256_context sha_ctx;
    mbedtls_sha256_init(&sha_ctx);
    mbedtls_sha256_starts(&sha_ctx, 0);  /* SHA-256 */
    mbedtls_sha256_update(&sha_ctx,
                           (uint8_t *)(firmware_addr + sizeof(firmware_header_t)),
                           header->size);
    mbedtls_sha256_finish(&sha_ctx, hash);
    mbedtls_sha256_free(&sha_ctx);

    /* Verify RSA signature */
    mbedtls_rsa_context rsa;
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V15, 0);

    /* Load public key from secure storage */
    load_public_key(&rsa, PUBLIC_KEY_ADDR);

    /* Verify signature */
    int ret = mbedtls_rsa_pkcs1_verify(&rsa,
                                        NULL, NULL,
                                        MBEDTLS_RSA_PUBLIC,
                                        MBEDTLS_MD_SHA256,
                                        32,
                                        hash,
                                        header->signature);

    mbedtls_rsa_free(&rsa);

    return (ret == 0);
}

void secure_boot_sequence(void) {
    /* Verify firmware signature */
    if (!verify_firmware_signature(FIRMWARE_START_ADDR)) {
        /* Signature verification failed - halt */
        while (1) {
            /* Flash error LED */
        }
    }

    /* Jump to verified firmware */
    uint32_t app_entry = *((uint32_t *)(FIRMWARE_START_ADDR + 4));
    void (*app_reset_handler)(void) = (void *)app_entry;

    /* Set vector table */
    SCB->VTOR = FIRMWARE_START_ADDR;

    /* Jump to application */
    app_reset_handler();
}
```

### 2. Cryptographic Implementation

**AES-128 Encryption (mbedTLS)**:
```c
#include "mbedtls/aes.h"
#include "mbedtls/gcm.h"

/* AES-GCM authenticated encryption */
status_t aes_gcm_encrypt(const uint8_t *key,        /* 128-bit key */
                          const uint8_t *iv,         /* 12-byte nonce */
                          const uint8_t *plaintext,
                          size_t plaintext_len,
                          uint8_t *ciphertext,
                          uint8_t *tag) {            /* 16-byte auth tag */

    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);

    /* Set key */
    int ret = mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, key, 128);
    if (ret != 0) {
        mbedtls_gcm_free(&gcm);
        return STATUS_ERROR;
    }

    /* Encrypt and authenticate */
    ret = mbedtls_gcm_crypt_and_tag(&gcm,
                                     MBEDTLS_GCM_ENCRYPT,
                                     plaintext_len,
                                     iv, 12,
                                     NULL, 0,  /* No additional data */
                                     plaintext,
                                     ciphertext,
                                     16, tag);

    mbedtls_gcm_free(&gcm);

    return (ret == 0) ? STATUS_OK : STATUS_ERROR;
}

/* AES-GCM authenticated decryption */
status_t aes_gcm_decrypt(const uint8_t *key,
                          const uint8_t *iv,
                          const uint8_t *ciphertext,
                          size_t ciphertext_len,
                          const uint8_t *tag,
                          uint8_t *plaintext) {

    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);

    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, key, 128);

    /* Decrypt and verify */
    int ret = mbedtls_gcm_auth_decrypt(&gcm,
                                        ciphertext_len,
                                        iv, 12,
                                        NULL, 0,
                                        tag, 16,
                                        ciphertext,
                                        plaintext);

    mbedtls_gcm_free(&gcm);

    /* ret == 0 means decryption AND authentication succeeded */
    return (ret == 0) ? STATUS_OK : STATUS_ERROR;
}
```

**ECDSA Signature Generation**:
```c
#include "mbedtls/ecdsa.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

status_t ecdsa_sign_message(const uint8_t *message, size_t msg_len,
                              const uint8_t *private_key,
                              uint8_t *signature, size_t *sig_len) {

    mbedtls_ecdsa_context ecdsa;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    uint8_t hash[32];

    /* Initialize */
    mbedtls_ecdsa_init(&ecdsa);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);

    /* Seed RNG */
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy, NULL, 0);

    /* Load private key (P-256) */
    mbedtls_ecp_group_load(&ecdsa.grp, MBEDTLS_ECP_DP_SECP256R1);
    mbedtls_mpi_read_binary(&ecdsa.d, private_key, 32);

    /* Hash message */
    mbedtls_sha256(message, msg_len, hash, 0);

    /* Sign */
    int ret = mbedtls_ecdsa_write_signature(&ecdsa,
                                             MBEDTLS_MD_SHA256,
                                             hash, 32,
                                             signature, sig_len,
                                             mbedtls_ctr_drbg_random,
                                             &ctr_drbg);

    /* Cleanup */
    mbedtls_ecdsa_free(&ecdsa);
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);

    return (ret == 0) ? STATUS_OK : STATUS_ERROR;
}
```

### 3. TLS/DTLS Secure Communication

**mbedTLS TLS Client**:
```c
#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

typedef struct {
    mbedtls_net_context net_ctx;
    mbedtls_ssl_context ssl;
    mbedtls_ssl_config conf;
    mbedtls_x509_crt cacert;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_entropy_context entropy;
} tls_client_t;

status_t tls_client_connect(tls_client_t *client, const char *host, const char *port) {
    int ret;

    /* Initialize structures */
    mbedtls_net_init(&client->net_ctx);
    mbedtls_ssl_init(&client->ssl);
    mbedtls_ssl_config_init(&client->conf);
    mbedtls_x509_crt_init(&client->cacert);
    mbedtls_ctr_drbg_init(&client->ctr_drbg);
    mbedtls_entropy_init(&client->entropy);

    /* Seed RNG */
    ret = mbedtls_ctr_drbg_seed(&client->ctr_drbg,
                                 mbedtls_entropy_func,
                                 &client->entropy,
                                 NULL, 0);
    if (ret != 0) {
        return STATUS_ERROR;
    }

    /* Load CA certificate */
    ret = mbedtls_x509_crt_parse(&client->cacert,
                                  (const unsigned char *)ca_cert_pem,
                                  strlen(ca_cert_pem) + 1);
    if (ret != 0) {
        return STATUS_ERROR;
    }

    /* Connect to server */
    ret = mbedtls_net_connect(&client->net_ctx, host, port, MBEDTLS_NET_PROTO_TCP);
    if (ret != 0) {
        return STATUS_ERROR;
    }

    /* Setup SSL/TLS */
    mbedtls_ssl_config_defaults(&client->conf,
                                 MBEDTLS_SSL_IS_CLIENT,
                                 MBEDTLS_SSL_TRANSPORT_STREAM,
                                 MBEDTLS_SSL_PRESET_DEFAULT);

    mbedtls_ssl_conf_ca_chain(&client->conf, &client->cacert, NULL);
    mbedtls_ssl_conf_rng(&client->conf, mbedtls_ctr_drbg_random, &client->ctr_drbg);

    /* Verify peer certificate */
    mbedtls_ssl_conf_authmode(&client->conf, MBEDTLS_SSL_VERIFY_REQUIRED);

    /* Setup SSL context */
    mbedtls_ssl_setup(&client->ssl, &client->conf);
    mbedtls_ssl_set_hostname(&client->ssl, host);
    mbedtls_ssl_set_bio(&client->ssl, &client->net_ctx,
                         mbedtls_net_send, mbedtls_net_recv, NULL);

    /* Perform TLS handshake */
    while ((ret = mbedtls_ssl_handshake(&client->ssl)) != 0) {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ &&
            ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
            return STATUS_ERROR;
        }
    }

    /* Verify certificate */
    uint32_t flags = mbedtls_ssl_get_verify_result(&client->ssl);
    if (flags != 0) {
        return STATUS_ERROR;
    }

    return STATUS_OK;
}

status_t tls_client_write(tls_client_t *client, const uint8_t *data, size_t len) {
    int ret = mbedtls_ssl_write(&client->ssl, data, len);
    return (ret > 0) ? STATUS_OK : STATUS_ERROR;
}

status_t tls_client_read(tls_client_t *client, uint8_t *buffer, size_t buf_len, size_t *read_len) {
    int ret = mbedtls_ssl_read(&client->ssl, buffer, buf_len);
    if (ret > 0) {
        *read_len = ret;
        return STATUS_OK;
    }
    return STATUS_ERROR;
}
```

### 4. Secure Key Storage

**ARM TrustZone Secure Storage**:
```c
/* Secure key storage in TrustZone secure world */
typedef struct {
    uint8_t aes_key[32];      /* AES-256 key */
    uint8_t ecc_private[32];  /* ECC P-256 private key */
    uint8_t device_id[16];    /* Unique device ID */
} secure_keys_t;

/* Secure function (runs in Secure state) */
__attribute__((cmse_nonsecure_entry))
status_t secure_get_aes_key(uint8_t *key_out) {
    /* Access secure key storage */
    secure_keys_t *keys = (secure_keys_t *)SECURE_KEY_STORAGE_ADDR;

    /* Copy key to non-secure memory */
    memcpy(key_out, keys->aes_key, 32);

    return STATUS_OK;
}

/* Non-secure call from normal world */
void encrypt_data_with_secure_key(uint8_t *data, size_t len) {
    uint8_t key[32];

    /* Request key from secure world */
    status_t status = secure_get_aes_key(key);

    if (STATUS_OK == status) {
        /* Use key for encryption */
        aes_encrypt(key, data, len);

        /* Zero key from memory */
        memset(key, 0, sizeof(key));
    }
}
```

**ATECC608 Secure Element**:
```c
#include "cryptoauthlib.h"

#define DEVICE_PRIVATE_KEY_SLOT  0

status_t atecc608_sign_message(const uint8_t *message, size_t msg_len,
                                 uint8_t *signature) {
    ATCA_STATUS status;
    uint8_t hash[32];

    /* Calculate SHA-256 */
    status = atcac_sw_sha2_256(message, msg_len, hash);
    if (status != ATCA_SUCCESS) {
        return STATUS_ERROR;
    }

    /* Sign with private key stored in slot 0 */
    status = atcab_sign(DEVICE_PRIVATE_KEY_SLOT, hash, signature);

    return (status == ATCA_SUCCESS) ? STATUS_OK : STATUS_ERROR;
}

status_t atecc608_generate_random(uint8_t *random_bytes, size_t len) {
    /* Generate true random number from hardware RNG */
    ATCA_STATUS status = atcab_random(random_bytes);

    return (status == ATCA_SUCCESS) ? STATUS_OK : STATUS_ERROR;
}
```

### 5. Secure OTA Firmware Updates

**Signed & Encrypted OTA**:
```c
typedef struct {
    uint32_t version;
    uint32_t size;
    uint8_t signature[64];  /* ECDSA signature */
    uint8_t iv[16];         /* AES-GCM IV */
} ota_header_t;

status_t ota_verify_and_decrypt(const uint8_t *encrypted_firmware,
                                  size_t fw_size,
                                  uint8_t *decrypted_firmware) {
    ota_header_t *header = (ota_header_t *)encrypted_firmware;
    uint8_t hash[32];

    /* Verify signature */
    mbedtls_sha256(encrypted_firmware + sizeof(ota_header_t),
                    header->size, hash, 0);

    if (!ecdsa_verify(hash, 32, header->signature, public_key)) {
        return STATUS_ERROR;  /* Invalid signature */
    }

    /* Decrypt firmware */
    uint8_t key[32];
    secure_get_ota_key(key);

    status_t status = aes_gcm_decrypt(key,
                                       header->iv,
                                       encrypted_firmware + sizeof(ota_header_t),
                                       header->size,
                                       decrypted_firmware);

    /* Zero key */
    memset(key, 0, sizeof(key));

    return status;
}

void ota_apply_update(void) {
    uint8_t *decrypted_fw = malloc(OTA_MAX_SIZE);

    if (ota_verify_and_decrypt(ota_buffer, ota_size, decrypted_fw) == STATUS_OK) {
        /* Write to flash */
        flash_erase(APPLICATION_ADDR, OTA_MAX_SIZE);
        flash_write(APPLICATION_ADDR, decrypted_fw, ota_size);

        /* Verify written firmware */
        if (verify_firmware_signature(APPLICATION_ADDR)) {
            /* Set boot flag to new firmware */
            set_boot_partition(APPLICATION_PARTITION);

            /* Reboot */
            NVIC_SystemReset();
        }
    }

    free(decrypted_fw);
}
```

---

## Security Best Practices

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimize access rights
3. **Secure by Default**: Security enabled out-of-box
4. **Input Validation**: Sanitize all external inputs
5. **Fail Securely**: Default to secure state on error
6. **Regular Updates**: OTA security patches

---

## Compliance Standards

- **IEC 62443**: Industrial automation security
- **ETSI EN 303 645**: Consumer IoT security
- **NIST CSF**: Cybersecurity Framework
- **OWASP Top 10**: IoT vulnerabilities
- **ISO 27001**: Information security management

---

## References

- ARM PSA Certified
- mbedTLS documentation
- NIST Special Publications (800-series)
- IoT Security Foundation guidelines

---

**Implement defense-in-depth security for IoT devices with cryptographic integrity, secure boot, and encrypted communication.**
