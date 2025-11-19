using UnityEngine;

/// <summary>
/// Production-ready player controller with movement, jumping, and camera control.
/// Demonstrates Unity best practices: component caching, state management, input handling.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    #region Serialized Fields

    [Header("Movement")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float sprintSpeed = 8f;
    [SerializeField] private float jumpHeight = 2f;
    [SerializeField] private float gravity = -9.81f;

    [Header("Camera")]
    [SerializeField] private Transform cameraTransform;
    [SerializeField] private float mouseSensitivity = 2f;
    [SerializeField] private float cameraMinY = -60f;
    [SerializeField] private float cameraMaxY = 60f;

    [Header("Ground Check")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private float groundDistance = 0.4f;
    [SerializeField] private LayerMask groundMask;

    #endregion

    #region Private Fields

    private CharacterController controller;
    private Vector3 velocity;
    private bool isGrounded;
    private float cameraRotationX = 0f;

    #endregion

    #region Unity Lifecycle

    private void Awake()
    {
        // Cache component reference
        controller = GetComponent<CharacterController>();

        // Validate serialized fields
        if (cameraTransform == null)
        {
            Debug.LogError($"{name}: Camera transform not assigned!", this);
        }

        if (groundCheck == null)
        {
            Debug.LogWarning($"{name}: Ground check not assigned. Creating default.", this);
            groundCheck = new GameObject("GroundCheck").transform;
            groundCheck.SetParent(transform);
            groundCheck.localPosition = new Vector3(0, -1f, 0);
        }

        // Lock and hide cursor
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void Update()
    {
        HandleGroundCheck();
        HandleMovement();
        HandleJump();
        HandleMouseLook();
    }

    #endregion

    #region Movement & Input

    private void HandleGroundCheck()
    {
        // Check if player is grounded using sphere cast
        isGrounded = Physics.CheckSphere(groundCheck.position, groundDistance, groundMask);

        // Reset vertical velocity when grounded
        if (isGrounded && velocity.y < 0)
        {
            velocity.y = -2f;  // Small negative value to stay grounded
        }
    }

    private void HandleMovement()
    {
        // Get input
        float horizontal = Input.GetAxisRaw("Horizontal");
        float vertical = Input.GetAxisRaw("Vertical");

        // Calculate movement direction relative to camera
        Vector3 forward = cameraTransform.forward;
        Vector3 right = cameraTransform.right;

        // Keep movement horizontal (ignore camera pitch)
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        Vector3 moveDirection = (forward * vertical + right * horizontal).normalized;

        // Apply sprint
        float currentSpeed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : moveSpeed;

        // Move character
        controller.Move(moveDirection * currentSpeed * Time.deltaTime);
    }

    private void HandleJump()
    {
        if (Input.GetButtonDown("Jump") && isGrounded)
        {
            // v = sqrt(2 * jumpHeight * gravity)
            velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);
        }

        // Apply gravity
        velocity.y += gravity * Time.deltaTime;

        // Move vertically
        controller.Move(velocity * Time.deltaTime);
    }

    private void HandleMouseLook()
    {
        // Get mouse input
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

        // Rotate player horizontally
        transform.Rotate(Vector3.up * mouseX);

        // Rotate camera vertically (with clamping)
        cameraRotationX -= mouseY;
        cameraRotationX = Mathf.Clamp(cameraRotationX, cameraMinY, cameraMaxY);
        cameraTransform.localRotation = Quaternion.Euler(cameraRotationX, 0f, 0f);
    }

    #endregion

    #region Debug Visualization

    private void OnDrawGizmosSelected()
    {
        if (groundCheck != null)
        {
            // Visualize ground check sphere
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawWireSphere(groundCheck.position, groundDistance);
        }
    }

    #endregion

    #region Public API

    /// <summary>
    /// Get current movement speed (useful for animations, etc.)
    /// </summary>
    public float GetCurrentSpeed()
    {
        Vector3 horizontalVelocity = new Vector3(controller.velocity.x, 0, controller.velocity.z);
        return horizontalVelocity.magnitude;
    }

    /// <summary>
    /// Check if player is currently grounded
    /// </summary>
    public bool IsGrounded => isGrounded;

    /// <summary>
    /// Get velocity vector
    /// </summary>
    public Vector3 Velocity => controller.velocity;

    #endregion
}
